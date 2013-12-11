from django import forms
from MyInfo.forms import ContactInformationForm

import logging
logger = logging.getLogger(__name__)

class AccountClaimLoginForm(forms.Form):
    id_number = forms.CharField(min_length=9, max_length=9, label="ID Number")
    birth_date = forms.DateField(label="Birth Date")
    auth_pass = forms.CharField(label="Password", widget=forms.PasswordInput())
    
class AcceptAUPForm(forms.Form):
    accepted = forms.BooleanField(label="I Accept")

# Must override __init__ to dynamically allocate choices for each user.
class OdinNameForm(forms.Form):
    def __init__(self, names, *args, **kwargs):
        super(OdinNameForm, self).__init__(*args, **kwargs)
        self.fields["name"] = forms.ChoiceField(choices=names, label="Odin Username")
                
class EmailAliasForm(forms.Form):
    def __init__(self, names, *args, **kwargs):
        super(EmailAliasForm, self).__init__(*args, **kwargs)
        self.fields["alias"] = forms.ChoiceField(choices=names, label="Email Alias")

class ContactInformationWithOptOutForm(ContactInformationForm):
    opt_out = forms.BooleanField(required=False, label="Opt Out")
    
    def clean(self):
        cleaned_data = super(ContactInformationWithOptOutForm, self).clean()
        
        email = cleaned_data.get("alternate_email")
        cell_number = cleaned_data.get("cell_phone")
        opt_out = cleaned_data.get('opt_out')
        
        
        if opt_out is False and email =='' and cell_number == '':
            raise forms.ValidationError('You must provide a valid password reset method or opt out of password resets.')
        
        return cleaned_data