from django.contrib import admin
from .models import Person, Credential, Issuance

# Register your models here.


admin.site.register(Person)
admin.site.register(Credential)
admin.site.register(Issuance)