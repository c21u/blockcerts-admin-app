from django.core.management.base import BaseCommand
from datetime import datetime
import random
from uuid import uuid4

from issuer.models import Credential, Issuance, Person, CertMailerConfig, PersonIssuances, CertToolsConfig


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_database()
        self.stdout.write('Seeding the database...')
        cert_mailer_config = create_cert_mailer_config()
        cert_tools_config = create_cert_tools_config()
        credential = create_credential(cert_tools_config, cert_mailer_config)
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


def create_cert_tools_config():
    cert_tools_config = CertToolsConfig(
        name='default',
        issuer_url='https://example.com',
        issuer_email='issuer@example.com',
        issuer_name='Example University',
        issuer_id='https://issuer.example.com',
        revocation_list='https://issuer.example.com/revocations.json',
        issuer_public_key='ecdsa-koblitz-pubkey:mtYhLaFbZbio7m4whmKX8jbV91J3ABnjVo',
        display_html_template=("<div style='font-family:Helvetica, sans-serif;'><h1>$title</h1><h2>ISSUED TO $name</h2>"
                               "<h2>ISSUED ON $date_issue</h2><h3>DESCRIPTION</h3><p>$description</p><h3>ISSUER</h3><p>$issuing_department</p></div>")
    )
    cert_tools_config.save()
    return cert_tools_config


def create_credential(cert_tools_config, cert_mailer_config):
    topics = ['AI', 'Basketweaving']
    events = ['Seminar', 'Workshop']
    issuing_department = 'C21U'

    credential = Credential(
        cert_tools_config=cert_tools_config,
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
        url_id=uuid4().hex[:6].upper()
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
