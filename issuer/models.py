from django.db import models
from django.utils import timezone
from uuid import uuid4
# Create your models here.


def get_uuid():
    return str(uuid4())


class CertMailerConfig(models.Model):
    name = models.CharField(max_length=50)
    mailer = models.CharField(max_length=50, choices=(("stdout", "Log instead of mailing"), ("mandrill", "Mailchimp Mandrill"), ("sendgrid", "Sendgrid")))
    from_email = models.CharField(max_length=100)
    introduction_email_subject = models.CharField(max_length=250)
    introduction_email_body = models.TextField()
    cert_email_subject = models.CharField(max_length=100)
    cert_email_body = models.TextField()

    def __str__(self):
        return self.name


class Credential(models.Model):
    title = models.TextField()
    description = models.TextField()
    narrative = models.TextField()
    issuing_department = models.CharField(max_length=50)
    cert_mailer_config = models.ForeignKey(CertMailerConfig, on_delete=models.CASCADE)
    badge_id = models.TextField(default=get_uuid)

    def __str__(self):
        return self.title


class Issuance(models.Model):
    date_issue = models.DateField()
    certificate_template = models.TextField(default='')
    url_id = models.TextField(default='')
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)
    people = models.ManyToManyField('Person', through='PersonIssuances', related_name='issuance')

    def ready_count(self):
        return self.people.exclude(public_address='').count() - self.issued_count()

    def unready_count(self):
        return self.people.filter(public_address='').count()

    def issued_count(self):
        return self.personissuances_set.filter(is_issued=True).count()

    def __str__(self):
        return f'{self.credential.title}: {self.date_issue}'


class Person(models.Model):
    class Meta:
        ordering = ('last_name',)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(db_index=True, max_length=250)
    email = models.EmailField(unique=True)
    public_address = models.CharField(max_length=250, default='')
    nonce = models.CharField(max_length=50, blank=True, null=True, unique=True)
    add_issuer_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class CertToolsConfig(models.Model):
    config = models.TextField()


class PersonIssuances(models.Model):
    class Meta:
        ordering = ('person__last_name',)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    issuance = models.ForeignKey(Issuance, on_delete=models.CASCADE)
    is_issued = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    unsigned_certificate = models.TextField(default='')
    last_reminded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.person}: {self.issuance}'
