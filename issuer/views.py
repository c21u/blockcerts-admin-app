from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.db.models.base import ObjectDoesNotExist

from .models import Person, Credential

import json
import uuid

# Create your views here.


class PersonView(View):
    def put(self, request):
        person_data = json.loads(request.body.decode('utf-8'))
        if not Person.objects.filter(email=person_data['email']).exists():
            self.add_new_person(person_data)
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
        _, created = Person.objects.get_or_create(
            first_name=person['first_name'],
            last_name=person['last_name'],
            email=person['email'],
            nonce=nonce
        )

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