from django.core.management.base import BaseCommand
from datetime import datetime
import random
from uuid import uuid4

from issuer.models import Credential, Issuance, Person, CertMailerConfig, PersonIssuances


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_database()
        self.stdout.write('Seeding the database...')
        cert_mailer_config = create_cert_mailer_config()
        credential = create_credential(cert_mailer_config)
        issuance = create_issuance(credential)
        create_person_issuance(create_person(), issuance)
        create_person_issuance(create_person(), issuance)
        create_person_issuance(create_person(), issuance)
        self.stdout.write('Seeding database completed.')

def create_cert_mailer_config():
    cert_mailer_config = CertMailerConfig(
        name="default",
        mailer="stdout",
        from_email="noreply@example.com"
    )
    cert_mailer_config.save()
    return cert_mailer_config


def create_credential(cert_mailer_config):
    topics = ['AI', 'Basketweaving']
    events = ['Seminar', 'Workshop']
    issuing_department = 'C21U'

    credential = Credential(
        cert_mailer_config=cert_mailer_config,
        title=random.choice(topics) + ' ' + random.choice(events),
        issuing_department=issuing_department,
        badge_id=str(uuid4())
    )
    credential.save()
    return credential


def create_issuance(credential):
    issuance = Issuance(
        credential_id=credential.id,
        date_issue=datetime.today(),
        url_id = uuid4().hex[:6].upper()
    )
    issuance.save()
    return issuance


def create_person():
    first_names = ['Chris', 'Emily', 'Matt', 'Stuart']
    last_names = ['East', 'North', 'South', 'West']

    person_first_name = random.choice(first_names)
    person_last_name = random.choice(last_names)
    person = Person(
        first_name=person_first_name,
        last_name=person_last_name,
        email=person_first_name.lower() + '.' + person_last_name.lower() + '@example.com'
    )
    person.save()
    return person


def create_person_issuance(person, issuance):
    person_issuance = PersonIssuances(person=person, issuance=issuance)
    person_issuance.save()


def clear_database():
    Person.objects.all().delete()
    Issuance.objects.all().delete()
    Credential.objects.all().delete()
    CertMailerConfig.objects.all().delete()
    PersonIssuances.objects.all().delete()
