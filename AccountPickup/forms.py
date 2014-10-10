from django import forms
from MyInfo.forms import ContactInformationForm

import logging
logger = logging.getLogger(__name__)

class AccountClaimLoginForm(forms.Form):
    id_number = forms.CharField(min_length=9, max_length=9, label="ID Number")
    birth_date = forms.DateField(label="Birth Date (MM/DD/YYYY)")
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