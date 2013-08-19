'''
Created on Mar 20, 2013

@author: hhauer

https://code.google.com/p/django-sms/
'''

from django import forms
from MyInfo.forms import formExternalContactInformation

import logging
logger = logging.getLogger(__name__)

class accountClaimLogin(forms.Form):
    id_number = forms.CharField(min_length=9, max_length=9, label="ID Number")
    birth_date = forms.DateField(label="Birth Date")
    auth_pass = forms.CharField(label="Password", widget=forms.PasswordInput())
    
class acceptAUP(forms.Form):
    accepted = forms.BooleanField(label="I Accept")

# The pickOdinNames class overrides the __init__ function in order to poll truename for the odin name
# options. This won't be necessary if we just assign an ODIN name.
class pickOdinName(forms.Form):
    def __init__(self, names, *args, **kwargs):
        super(pickOdinName, self).__init__(*args, **kwargs)
        self.fields["name"] = forms.ChoiceField(choices=names, label="Odin Username")
                
class EmailAliasForm(forms.Form):
    def __init__(self, names, *args, **kwargs):
        super(EmailAliasForm, self).__init__(*args, **kwargs)
        self.fields["aliases"] = forms.ChoiceField(choices=names, label="Email Alias")

class password_reset_optout_form(formExternalContactInformation):
    opt_out = forms.BooleanField(required=False, label="Opt Out")
    
    def clean(self):
        cleaned_data = super(password_reset_optout_form, self).clean()
        
        email = cleaned_data.get("alternate_email")
        cell_number = cleaned_data.get("cell_number")
        cell_carrier = cleaned_data.get("cell_carrier")
        opt_out = cleaned_data.get('opt_out')
        
        
        if opt_out is False and email =='' and (cell_number == '' or cell_carrier is None):
            raise forms.ValidationError('You must provide a valid password reset method or opt out of password resets.')
        
        return cleaned_data