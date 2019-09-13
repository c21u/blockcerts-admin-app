from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic, View

from .models import Person, Credential, Issuance, CertToolsConfig, PersonIssuances
from .forms import PersonForm, CredentialForm, IssuanceForm

import csv
import io
import json
import uuid
import concurrent.futures
from types import SimpleNamespace as Namespace
from cert_mailer import introduce
from string import Template
from cert_tools.create_v2_certificate_template import create_certificate_template
from cert_tools.instantiate_v2_certificate_batch import Recipient, create_unsigned_certificates_from_roster
from datetime import datetime


def recursive_namespace_to_dict(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], Namespace):
                obj[i] = obj[i].__dict__
            recursive_namespace_to_dict(obj[i])
    if isinstance(obj, dict):
        for key in obj:
            if isinstance(obj[key], Namespace):
                obj[key] = obj[key].__dict__
            recursive_namespace_to_dict(obj[key])


def send_invite(person, credential):
    mailer_config = credential.cert_mailer_config
    mailer_config.introduction_url = settings.ISSUER_URL
    person_email = {'first_name': person.first_name, 'email': person.email, 'nonce': person.nonce, 'title': credential.title}
    introduce.send_email(mailer_config, person_email)


def send_invites(people, credential):
    if len(people) > 0:
        with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
            def cred_gen():
                for n in range(len(people)):
                    yield credential
            executor.map(send_invite, people, cred_gen())


def add_new_person(person):
    nonce = uuid.uuid4().hex[:6].upper()
    while Person.objects.filter(nonce=nonce).exists():
        nonce = uuid.uuid4().hex[:6].upper()
    person, created = Person.objects.get_or_create(
        first_name=person['first_name'],
        last_name=person['last_name'],
        email=person['email'],
        nonce=nonce
    )
    return person


class HomePageView(View):
    def get(self, request):
        return render(request, 'index.html')


class AddPersonView(View):
    def get(self, request, issuance_id=None):
        person_form = PersonForm()
        return render(request, 'add_person.html', {'form': person_form, 'person_added': False, 'INSTITUTION_NAME': settings.INSTITUTION_NAME})

    def post(self, request, issuance_id=None):
        person_form = PersonForm(request.POST)
        person_was_added = False
        if person_form.is_valid():
            person_data = {}
            issuance = Issuance.objects.get(url_id=issuance_id)
            credential = issuance.credential
            person_data['first_name'] = person_form.cleaned_data['first_name']
            person_data['last_name'] = person_form.cleaned_data['last_name']
            person_data['email'] = person_form.cleaned_data['email']
            if not Person.objects.filter(email=person_data['email']).exists():
                person = add_new_person(person_data)
                send_invite(person, credential)
            else:
                person = Person.objects.get(email=person_data['email'])
            person_issuance, created = PersonIssuances.objects.get_or_create(
                person=person,
                issuance=issuance
            )
            person_form = PersonForm()
            person_was_added = True
        return render(request, 'add_person.html', {'form': person_form, 'person_added': person_was_added, 'INSTITUTION_NAME': settings.INSTITUTION_NAME})


class UpdatePersonView(View):
    def post(self, request):
        person_data = json.loads(request.body.decode('utf-8'))
        self.update_person(person_data)
        return HttpResponse('Added public address')

    def update_person(self, person):
        Person.objects.filter(nonce=person['nonce']).update(public_address=person['bitcoinAddress'], nonce=None)


class CredentialView(LoginRequiredMixin, View):
    def get(self, request):
        credential_form = CredentialForm()
        return render(request, 'add_credential.html', {'form': credential_form})

    def post(self, request):
        credential_form = CredentialForm(request.POST)
        if credential_form.is_valid():
            self.add_credential(credential_form.cleaned_data)
        credential_form = CredentialForm()
        return render(request, 'add_credential.html', {'form': credential_form})

    def add_credential(self, credential):
        credential, created = Credential.objects.get_or_create(
            title=credential['title'],
            description=credential['description'],
            narrative=credential['narrative'],
            issuing_department=credential['issuing_department'],
            cert_mailer_config=credential['cert_mailer_config']
        )


class UpdateCredentialView(LoginRequiredMixin, View):
    def get(self, request, id=None):
        credential = Credential.objects.get(id=id)
        credential_form = CredentialForm(instance=credential)
        return render(request, 'add_credential.html', {'form': credential_form})

    def post(self, request, id=None):
        credential_form = CredentialForm(request.POST, instance=Credential.objects.get(id=id))
        credential_form.save()
        return render(request, 'add_credential.html', {'form': credential_form})


class IssuanceView(LoginRequiredMixin, View):
    def get(self, request):
        issuance_form = IssuanceForm()
        return render(request, 'add_issuance.html', {'form': issuance_form, 'issuance_url': False})

    def post(self, request):
        issuance_data = {}
        issuance_post = request.POST
        issuance_data['credential_id'] = int(issuance_post.get('credential')[0])
        issuance_data['date_issue'] = datetime.strptime(issuance_post.get('date_issue'), '%m/%d/%Y')
        issuance = self.add_issuance(issuance_data)
        issuance_url = request.scheme + '://' + request.get_host() + '/' + str(issuance.url_id) + '/add_person/'
        linked_credential = Credential.objects.get(id=issuance_data['credential_id'])

        substitutions = {'title': linked_credential.title, 'narrative': linked_credential.narrative,
                         'description': linked_credential.description, 'issuing_department': linked_credential.issuing_department,
                         'badge_id': linked_credential.badge_id}
        cert_tools_config_data = CertToolsConfig.objects.all().first()
        cert_tools_config_data.config = Template(cert_tools_config_data.config).safe_substitute(substitutions)
        cert_tools_config = json.loads(cert_tools_config_data.config, object_hook=lambda d: Namespace(**d))
        recursive_namespace_to_dict(cert_tools_config.additional_global_fields)

        certificate_template = create_certificate_template(cert_tools_config)
        issuance.certificate_template = json.dumps(certificate_template)
        issuance.save()
        issuance_form = IssuanceForm()
        return render(request, 'add_issuance.html', {'form': issuance_form, 'issuance_url': issuance_url})

    def add_issuance(self, issuance):
        linked_credential = Credential.objects.get(id=issuance['credential_id'])
        url_id = uuid.uuid4().hex[:6].upper()
        while Issuance.objects.filter(url_id=url_id).exists():
            url_id = uuid.uuid4().hex[:6].upper()
        issuance, created = Issuance.objects.get_or_create(
            date_issue=issuance['date_issue'],
            url_id=url_id,
            credential=linked_credential
        )
        return issuance


class UnsignedCertificatesView(View):
    def post(self, request):
        cert_tools_config_data = CertToolsConfig.objects.all().first()
        cert_tools_config = json.loads(cert_tools_config_data.config, object_hook=lambda d: Namespace(**d))
        recursive_namespace_to_dict(cert_tools_config.additional_global_fields)
        for person_issuance in PersonIssuances.objects.filter(is_issued=False, is_approved=True).exclude(person__public_address=''):
            issuance = Issuance.objects.get(id=person_issuance.issuance.id)
            person = {
                      'name': f'{person_issuance.person.first_name} {person_issuance.person.last_name}',
                      'pubkey': f'ecdsa-koblitz-pubkey: {person_issuance.person.public_address}',
                      'identity': person_issuance.person.email}
            date_issue = datetime.now().strftime("%B %d, %Y")
            template = json.loads(Template(issuance.certificate_template).safe_substitute(name=person['name'], date_issue=date_issue))
            person = Recipient(person)

            usc = create_unsigned_certificates_from_roster(template,
                                                           [person], False,
                                                           cert_tools_config.additional_per_recipient_fields,
                                                           cert_tools_config.hash_emails)
            for uid in usc.keys():
                usc[uid]['id'] = settings.VIEW_URL.format(uid)

            person_issuance.unsigned_certificate = json.dumps(usc)
            person_issuance.save()
        return HttpResponse("DONE")


class ThankYouView(View):
    def get(self, request):
        return render(request, 'thankyou.html')


class ApproveRecipientsView(LoginRequiredMixin, generic.DetailView):
    model = Issuance
    template_name = "recipients/approve.html"

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        people_to_approve = data.getlist('people_to_approve')
        PersonIssuances.objects.filter(id__in=people_to_approve).update(is_approved=True)
        return render(request, 'recipients/approve_success.html', {'approved_count': len(people_to_approve)})


class CompletedRecipientsView(LoginRequiredMixin, generic.DetailView):
    model = Issuance
    template_name = "recipients/completed.html"


class InviteRecipientsView(LoginRequiredMixin, generic.DetailView):
    model = Issuance
    template_name = "recipients/invite.html"


class RemindRecipientsView(LoginRequiredMixin, generic.DetailView):
    model = Issuance
    template_name = "recipients/remind.html"

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        remind_list = data.getlist('people_to_remind')
        people_to_remind = Person.objects.filter(pk__in=remind_list)
        issuance = self.get_object()
        send_invites(people_to_remind, issuance.credential)
        return render(request, 'recipients/remind_success.html', {'reminded_count': len(people_to_remind)})


class ManageRecipientsView(LoginRequiredMixin, generic.ListView):
    model = Credential
    template_name = "recipients/manage.html"


class UploadCsvView(LoginRequiredMixin, View):
    def post(self, request):
        csv_file = request.FILES['csv_file']
        issuance = Issuance.objects.get(id=request.POST.get('issuance_id'))
        if csv_file.multiple_chunks():
            messages.error(request, f'Uploaded file is too big ({csv_file.size/(1000*1000)}.2f MB).')
            return HttpResponseRedirect(reverse('recipients/invite', args=[issuance.id]))

        people_to_invite = []
        with io.TextIOWrapper(csv_file, encoding='utf-8') as text_file:
            reader = csv.DictReader(text_file)
            for row in reader:
                if not Person.objects.filter(email=row['email']).exists():
                    person = add_new_person(row)
                    people_to_invite.append(person)
                else:
                    person = Person.objects.get(email=row['email'])
                approved = 'approved' in row and bool(row['approved'])
                person_issuance, created = PersonIssuances.objects.get_or_create(
                    person=person,
                    issuance=issuance,
                    is_approved=approved
                )
        send_invites(people_to_invite, issuance.credential)
        return HttpResponseRedirect(reverse('recipients/approve', args=[issuance.id]))
