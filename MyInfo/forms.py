from django import forms
from django_localflavor_us.forms import USPhoneNumberField
from MyInfo.models import Department, CellCarrier
from captcha.fields import ReCaptchaField

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
class formExternalContactInformation(forms.Form):
    alternate_email = forms.EmailField(max_length=254, label="Alternate Email", required=False)
    cell_number = USPhoneNumberField(label="Cell Phone #", required=False)
    cell_carrier = forms.ModelChoiceField(label="Cell Phone Carrier", queryset=CellCarrier.objects.all(), required=False)
    
    # Verify that they did not use an @pdx.edu address in the external email field.
    def clean_alternate_email(self):
        email = self.cleaned_data['alternate_email']
        
        if email.endswith('@pdx.edu'):
            raise forms.ValidationError("Alternate Email can not be an @pdx.edu address.")
        
        return email
    
    def clean(self):
        cleaned_data = super(formExternalContactInformation, self).clean()
        
        cell_number = cleaned_data.get("cell_number")
        cell_carrier = cleaned_data.get("cell_carrier")
        
        if (cell_number != '' and cell_carrier is None) or (cell_number == '' and cell_carrier is not None):
            raise forms.ValidationError('Cell phone and carrier are both required in order to send a text message.')
        
        return cleaned_data

# Information used by PSU Employees
class formPSUEmployee(forms.Form):
    job_title = forms.CharField(label="Job Title")
    office_building = forms.CharField(label="Office Building")
    office_room = forms.CharField(label="Office Room #")
    department = forms.ModelChoiceField(label="Department", queryset=Department.objects.all())
    
# Login for expired passwords.
class expired_password_login_form(forms.Form):
    odin_username = forms.CharField(label="Odin Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

# reCAPTCHA validation.
class ReCaptchaForm(forms.Form):
    captcha = ReCaptchaField()