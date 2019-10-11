from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic, View
from django.utils.html import strip_tags

from .models import Person, Credential, Issuance, PersonIssuances
from .forms import PersonForm, CredentialForm, IssuanceForm

import csv
import io
import json
import os
import uuid
import concurrent.futures
from types import SimpleNamespace as Namespace
from cert_mailer import introduce, sendcert
from string import Template
from cert_tools.create_v2_certificate_template import create_certificate_template
from cert_tools.instantiate_v2_certificate_batch import Recipient, create_unsigned_certificates_from_roster
from datetime import datetime
from itertools import repeat
import requests


def get_unsigned_credential(credential, person):
    cert_tools_config = credential.cert_tools_config
    template = Namespace()
    template.issuer_url = cert_tools_config.issuer_url
    template.issuer_email = cert_tools_config.issuer_email
    template.issuer_name = cert_tools_config.issuer_name
    template.issuer_id = cert_tools_config.issuer_id
    template.revocation_list = cert_tools_config.revocation_list
    template.issuer_public_key = cert_tools_config.issuer_public_key
    template.certificate_title = strip_tags(credential.title)
    template.certificate_description = strip_tags(credential.description)
    template.criteria_narrative = strip_tags(credential.narrative)
    template.badge_id = credential.badge_id
    template.issuer_signature_lines = None
    template.hash_emails = False
    template.additional_per_recipient_fields = None
    template.display_html = Template(cert_tools_config.display_html_template).safe_substitute(name=person.name,
                                                                                              date_issue=datetime.now().strftime("%B %d, %Y"),
                                                                                              description=credential.description,
                                                                                              issuing_department=credential.issuing_department,
                                                                                              narrative=credential.narrative)
    template.additional_global_fields = [{
        "path": "$.displayHtml",
        "value": template.display_html
        }, {
            "path": "$.@context",
            "value": [
                "https://w3id.org/openbadges/v2",
                "https://w3id.org/blockcerts/v2",
                {"displayHtml": {
                    "@id": "https://schemas.learningmachine.com/2017/blockcerts/displayHtml",
                    "@type": "https://schemas.learningmachine.com/2017/types/text/html"
                    }}
                ]
            }]
    template.issuer_logo_file = 'images/issuer-logo.png'
    template.cert_image_file = 'images/cert-image.png'
    template.abs_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'data'))
    template = create_certificate_template(template)
    usc = create_unsigned_certificates_from_roster(template, [person], False, None, False)
    for uid in usc.keys():
        usc[uid]['id'] = settings.VIEW_URL.format(uid)

    return usc


def send_invite(person, credential, is_reminder=False):
    mailer_config = credential.cert_mailer_config
    mailer_config.introduction_url = settings.ISSUER_URL
    if is_reminder:
        mailer_config.introduction_email_subject = mailer_config.remind_email_subject
        mailer_config.introduction_email_body = mailer_config.remind_email_body
    person_email = {'first_name': person.first_name, 'email': person.email, 'nonce': person.nonce, 'title': credential.title}
    introduce.send_email(mailer_config, person_email)


def send_invites(people, credential, is_reminder=False):
    if len(people) > 0:
        with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
            executor.map(send_invite, people, repeat(credential), repeat(is_reminder))

def send_issued_cert(person, credential, cert_filename):
    print("HERE")
    mailer_config = credential.cert_mailer_config
    mailer_config.introduction_url = settings.ISSUER_URL
    person_email = {'first_name': person.first_name, 'email': person.email, 'filename': cert_filename}
    sendcert.send_email(mailer_config, person_email)


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
        issuance_data['name'] = issuance_post.get('name')
        issuance = self.add_issuance(issuance_data)
        issuance_url = request.scheme + '://' + request.get_host() + '/' + str(issuance.url_id) + '/add_person/'

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
            name=issuance['name'],
            credential=linked_credential
        )
        return issuance

class IssueResponse(HttpResponse):
    def __init__(self, data, callback, **kwargs):
        super().__init__(data, **kwargs)
        self.callback = callback

    def close(self):
        super().close()
        self.callback()

class IssueCertificatesView(View):
    def post(self, request):
        unsigned_certs_batch = []
        for person_issuance in PersonIssuances.objects.filter(is_issued=False, is_approved=True).exclude(person__public_address=''):
            issuance = Issuance.objects.get(id=person_issuance.issuance.id)
            person = {
                      'name': f'{person_issuance.person.first_name} {person_issuance.person.last_name}',
                      'pubkey': f'ecdsa-koblitz-pubkey: {person_issuance.person.public_address}',
                      'identity': person_issuance.person.email}

            person = Recipient(person)
            usc = get_unsigned_credential(issuance.credential, person)
            person_issuance.unsigned_certificate = json.dumps(usc)
            for uid in usc.keys():
                person_issuance.cert_uid = uid
            unsigned_certs_batch.append(usc)
            person_issuance.save()
        signed_certs_batch = requests.post(settings.CERT_ISSUER_URL, json=unsigned_certs_batch).text
        return HttpResponse(signed_certs_batch)

        def process_signed_certs():
            for signed_cert in signed_certs_batch:
                for uid in signed_cert:
                    person_issuance = PersonIssuances.objects.get(cert_uid=uid)
                    print("ABOUT TO SEND")
                    send_issued_cert(person_issuance.person, person_issuance.issuance.credential, uid + '.json')

        return IssueResponse(signed_certs_batch, process_signed_certs, status=200)



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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_personissuances'] = (
            context['issuance'].personissuances_set.filter(is_approved=True,
                                                           is_issued=True))
        return context

class InviteRecipientsView(LoginRequiredMixin, generic.DetailView):
    model = Issuance
    template_name = "recipients/invite.html"


class RemindRecipientsView(LoginRequiredMixin, generic.DetailView):
    model = Issuance
    template_name = "recipients/remind.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['institution_name'] = settings.INSTITUTION_NAME
        context['approved_count'] = context['issuance'].personissuances_set.filter(is_approved=True).count()
        context['unapproved_count'] = context['issuance'].personissuances_set.filter(is_approved=False).count()
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        remind_list = data.getlist('people_to_remind')
        people_to_remind = Person.objects.filter(pk__in=remind_list)
        issuance = self.get_object()
        send_invites(people_to_remind, issuance.credential, True)
        return render(request, 'recipients/remind_success.html', {'reminded_count': len(people_to_remind)})


class ManageCredentialsView(LoginRequiredMixin, generic.ListView):
    model = Credential
    template_name = "manageCredentials.html"


class UploadCsvView(LoginRequiredMixin, View):
    def post(self, request):
        csv_file = request.FILES['csv_file']
        issuance = Issuance.objects.get(id=request.POST.get('issuance_id'))
        if csv_file.multiple_chunks():
            messages.error(request, f'Uploaded file is too big ({csv_file.size/(1000*1000)}.2f MB).')
            return HttpResponseRedirect(reverse('recipients/invite', args=[issuance.id]))

        people_to_invite = []

        # The utf-8-sig encoding will gracefully handle a BOM if present.
        with io.TextIOWrapper(csv_file, encoding='utf-8-sig') as text_file:
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
