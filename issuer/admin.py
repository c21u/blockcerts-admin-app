from django.contrib import admin
from .models import Person, Credential, Issuance, CertMailerConfig, CertToolsConfig, PersonIssuances


class PersonIssuancesInline(admin.TabularInline):
    model = PersonIssuances
    can_delete = False
    extra = 0

    """ Set all fields that will appear on the Person admin page to read-only. """
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonIssuancesInline,)


admin.site.register(Person, PersonAdmin)
admin.site.register(Credential)
admin.site.register(Issuance)
admin.site.register(CertMailerConfig)
admin.site.register(CertToolsConfig)
admin.site.register(PersonIssuances)
