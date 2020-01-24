from django import forms
from bootstrap_datepicker_plus import DatePickerInput

from .models import Credential


class PersonForm(forms.Form):
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'id': 'first_name'}))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'id': 'last_name'}))
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'id': 'email'}))


class CredentialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(CredentialForm, self).__init__(*args, **kwargs)
        if not self.user.is_superuser:
            self.fields["issuing_department"].queryset = self.user.groups

    def clean_issuing_department(self):
        issuing_department = self.cleaned_data.get("issuing_department")
        if self.user and (self.user.is_superuser or self.user.groups.filter(pk=issuing_department).exists()):
            return issuing_department
        raise forms.ValidationError("User is not a member of the issuing_department")

    class Meta:
        model = Credential
        fields = ["title", "description", "narrative", "issuing_department", "cert_mailer_config", "cert_tools_config"]


class IssuanceForm(forms.Form):
    date_issue = forms.DateField(label='Issue Date', widget=DatePickerInput())
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'id': 'name'}), required=False)

    def __init__(self):
        super(IssuanceForm, self).__init__()
        credentials = Credential.objects.values_list('id', 'title')
        credential = forms.CharField(label='Credential', widget=forms.Select(choices=credentials))
        self.fields['credential'] = credential
