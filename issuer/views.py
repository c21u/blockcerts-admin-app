from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.db.models.base import ObjectDoesNotExist

from .models import Person, Credential, Issuance

import json
import uuid
from cert_mailer import introduce
import os
import urllib
# Create your views here.


class PersonView(View):
    def put(self, request):
        person_data = json.loads(request.body.decode('utf-8'))
        if not Person.objects.filter(email=person_data['email']).exists():
            created_person = self.add_new_person(person_data)
            mailer_config = introduce.get_config(os.getcwd() + '/cert-mailer/conf.ini')
            # intro_url = urllib.quote(mailer_config.introduction_url, safe=':')
            # print(mailer_config.introduction_url)
            created_person = {'first_name':created_person.first_name, 'email':created_person.email, 'nonce':created_person.nonce}
            introduce.send_emails(mailer_config, created_person)
            return HttpResponse('Created new person')
        else:
            return HttpResponse('Person already exists')

    def post(self, request):
        person_data = json.loads(request.body.decode('utf-8'))
        self.update_person(person_data)
        return HttpResponse('Added public address')

    def add_new_person(self, person):
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


    def update_person(self, person):
        Person.objects.filter(nonce=person['nonce']).update(public_address=person['public_address'])


class CredentialView(View):
    def put(self, request):
        credential_data = json.loads(request.body.decode('utf-8'))
        credential_id = self.add_credential(credential_data)
        return JsonResponse({'credential_id':credential_id})

    def add_credential(self, credential):
        credential, created = Credential.objects.get_or_create(
            title=credential['title'],
            description=credential['description'],
            narrative=credential['narrative'],
            issuing_department=credential['issuing_department']
        )
        return credential.id


class IssuanceView(View):
    def put(self, request):
        issuance_data = json.loads(request.body.decode('utf-8'))
        issuance_id = self.add_issuance(issuance_data)
        return JsonResponse({'issuance_link':issuance_id})

    def add_issuance(self, issuance):
        linked_credential = Credential.objects.get(id=issuance['credential_id'])
        issuance, created = Issuance.objects.get_or_create(
            date_issue=issuance['date'],
            credential=linked_credential
        )
        issuance.associated_filename = (str(issuance.id) + '_' + issuance.date_issue.strftime("%Y/%m/%d")).replace('/', '_')
        issuance.save()
        return issuance.id