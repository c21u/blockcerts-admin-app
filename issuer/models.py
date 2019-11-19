from django.db import models
from django.utils import timezone
from uuid import uuid4
# Create your models here.


def get_uuid():
    return str(uuid4())


class CertToolsConfig(models.Model):
    name = models.CharField(max_length=50)
    issuer_url = models.URLField()
    issuer_email = models.EmailField()
    issuer_name = models.CharField(max_length=250)
    issuer_id = models.URLField()
    revocation_list = models.URLField()
    issuer_public_key = models.CharField(max_length=60)
    display_html_template = models.TextField()

    def __str__(self):
        return self.name


class CertMailerConfig(models.Model):
    name = models.CharField(max_length=50)
    mailer = models.CharField(max_length=50, choices=(("stdout", "Log instead of mailing"), ("mandrill", "Mailchimp Mandrill"), ("sendgrid", "Sendgrid")))
    from_email = models.CharField(max_length=100)
    introduction_email_subject = models.CharField(max_length=250)
    introduction_email_body = models.TextField()
    cert_email_subject = models.CharField(max_length=100)
    cert_email_body = models.TextField()
    remind_email_subject = models.CharField(max_length=250)
    remind_email_body = models.TextField()

    def __str__(self):
        return self.name


class Credential(models.Model):
    title = models.TextField()
    description = models.TextField()
    narrative = models.TextField()
    issuing_department = models.CharField(max_length=50)
    cert_mailer_config = models.ForeignKey(CertMailerConfig, on_delete=models.CASCADE)
    cert_tools_config = models.ForeignKey(CertToolsConfig, on_delete=models.CASCADE)
    badge_id = models.TextField(default=get_uuid)

    def __str__(self):
        return self.title


class Issuance(models.Model):
    name = models.TextField(default='')
    date_issue = models.DateField()
    url_id = models.TextField(default='')
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)
    people = models.ManyToManyField('Person', through='PersonIssuances', related_name='issuance')

    def ready_count(self):
        return self.people.exclude(public_address='').count() - self.issued_count()

    def unready_count(self):
        return self.people.filter(public_address='').count()

    def issued_count(self):
        return self.personissuances_set.filter(is_issued=True).count()

    def approved_count(self):
        return self.personissuances_set.filter(is_approved=True).count()

    def __str__(self):
        separator = ''
        if self.name:
            separator = ': '
        return f'{self.name}{separator}{self.date_issue}'


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


class PersonIssuances(models.Model):
    class Meta:
        ordering = ('person__last_name',)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    issuance = models.ForeignKey(Issuance, on_delete=models.CASCADE)
    is_issued = models.BooleanField(default=False)
    issued_at = models.DateField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateField(default=timezone.now)
    last_reminded_at = models.DateTimeField(default=timezone.now)
    cert_uid = models.TextField(default='')

    def __str__(self):
        return f'{self.person}: {self.issuance}'
