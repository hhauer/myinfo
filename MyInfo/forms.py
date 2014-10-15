from django import forms

from localflavor.us.forms import USZipCodeField

from MyInfo.models import DirectoryInformation, ContactInformation

import logging
logger = logging.getLogger(__name__)

class formNewPassword(forms.Form):
    newPassword = forms.CharField(max_length=32, widget=forms.PasswordInput, label="New Password")
    confirmPassword = forms.CharField(max_length=32, widget=forms.PasswordInput, label="Confirm Password")
    
    # Validate that the passwords match.
    def clean_confirmPassword(self):
        password1 = self.cleaned_data.get("newPassword", "")
        password2 = self.cleaned_data["confirmPassword"]
        
        if password1 != password2:
            raise forms.ValidationError("The two passwords didn't match.")
        
        return password2

class formPasswordChange(formNewPassword):
    currentPassword = forms.CharField(max_length=32, widget=forms.PasswordInput, label="Current Password")
    
    # Manually set the order of fields so that "Current Password" comes first
    def __init__(self, *args, **kwargs):
        super(formPasswordChange, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['currentPassword', 'newPassword', 'confirmPassword']

# Contact information used for resetting passwords.   
class ContactInformationForm(forms.ModelForm):
    
    class Meta:
        model = ContactInformation
        fields = ['alternate_email', 'cell_phone']

    def clean(self):
        cleaned_data = super(ContactInformationForm, self).clean()

        email = cleaned_data.get('alternate_email')
        phone = cleaned_data.get('cell_phone')

        if email == "" and phone == "":
            raise forms.ValidationError("Must provide either an alternate email address or text-capable phone number.")

        return cleaned_data
    
    # Verify that they did not use an @pdx.edu address in the external email field.
    def clean_alternate_email(self):
        email = self.cleaned_data['alternate_email']
        
        if email.endswith('@pdx.edu'):
            raise forms.ValidationError("Alternate Email can not be an @pdx.edu address.")
        
        return email

# Information used by PSU Employees
class DirectoryInformationForm(forms.ModelForm):
    class Meta:
        model = DirectoryInformation
        exclude = ['psu_uuid',]
    
# Main MyInfo login form.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, label="Odin Username or PSU ID Number")
    password = forms.CharField(max_length=32, label="Password", widget=forms.PasswordInput())