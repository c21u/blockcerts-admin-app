from django.contrib import admin
from .models import User, Credential, Issuance

# Register your models here.


admin.site.register(User)
admin.site.register(Credential)
admin.site.register(Issuance)