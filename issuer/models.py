from django.db import models

# Create your models here.


class Credential(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    issuing_department = models.CharField(max_length=50)


class Issuance(models.Model):
    date_issue = models.DateField()
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)


class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    otc = models.CharField(max_length=50, unique=True)
    blockchain_address = models.CharField(max_length=50, unique=True)
    add_issuer_timestamp = models.DateTimeField()
    # issuances = models.ManyToManyField(Issuance, default=None)


class UserIssuances(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issuance = models.ForeignKey(Issuance, on_delete=models.CASCADE)
    isIssued = models.BooleanField()