from django import forms
from django_localflavor_us.forms import USPhoneNumberField

import logging
logger = logging.getLogger(__name__)

class request_reset_form(forms.Form):
    email = forms.EmailField(label="Email Address", required=False)
    cell = USPhoneNumberField(label="-OR- Cell #", required=False)
    
        # Verify that they did not use an @pdx.edu address in the external email field.
    def clean_email(self):
        email = self.cleaned_data['email']
        
        if email.endswith('@pdx.edu'):
            raise forms.ValidationError("Can not reset with an @pdx.edu address. Please use your personal email address.")
        
        return email
    
    def clean(self):
        cleaned_data = super(request_reset_form, self).clean()
        
        email = cleaned_data.get("email")
        cell = cleaned_data.get("cell")
        
        if email == '' and cell == '':
            raise forms.ValidationError('You must provide either an email or cell # to send a reset token to.')
        
        return cleaned_data
    
class token_form(forms.Form):
    token = forms.CharField(label="Reset Token")