from django import forms
from bootstrap_datepicker_plus import DatePickerInput

from .models import Credential


class PersonForm(forms.Form):
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'id': 'first_name'}))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'id' : 'last_name'}))
    email = forms.CharField(label='Email', widget=forms.TextInput(attrs={'id': 'email'}))


class CredentialForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label='Description')
    narrative = forms.CharField(label='Narrative')
    issuing_department = forms.CharField(label='Issuing Department')


class IssuanceForm(forms.Form):
    date_issue = forms.DateField(label='Issue Date', widget=DatePickerInput())

    def __init__(self):
        super(IssuanceForm, self).__init__()
        credentials = Credential.objects.values_list('id', 'title')
        credential = forms.CharField(label='Credential', widget=forms.Select(choices=credentials))
        self.fields['credential'] = credential