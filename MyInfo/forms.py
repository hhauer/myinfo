from collections import OrderedDict
from django import forms

from MyInfo.models import DirectoryInformation, ContactInformation
from django.contrib.auth.forms import SetPasswordForm
from lib.api_calls import change_password

import logging
logger = logging.getLogger(__name__)


class SetOdinPasswordForm(SetPasswordForm):

    def __init__(self, user, *args, **kwargs):
        super(SetOdinPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields['new_password1'].min_length = 8
        self.fields['new_password1'].max_length = 30
        self.fields['new_password2'].min_length = 8
        self.fields['new_password2'].max_length = 30

    def clean(self):
        super(SetOdinPasswordForm, self).clean()
        # Consider checking status router and existence of current_password field to make sure the proper
        # form is being used
        if len(self._errors) == 0:
            new_pw = self.cleaned_data['new_password1']
            old_pw = self.cleaned_data.get('current_password', None)
            identity = {'PSU_UUID': self.user.get_username()}

            (status, errors) = change_password(identity=identity, new_password=new_pw, old_password=old_pw)

            if status is False:
                raise forms.ValidationError([forms.ValidationError(error) for error in errors])
            else:
                # Password is not stored in user object, but new hash is needed for auth purposes
                self.user.set_unusable_password()
                self.user.save(update_fields=['password'])

    def save(self, commit=True):
        pass


class ChangeOdinPasswordForm(SetOdinPasswordForm):
    current_password = forms.CharField(
        min_length=8, max_length=30, widget=forms.PasswordInput, label="Current password")

    # Field ordering, not valid code until django 1.8
    # field_order = ['current_password', 'new_password1', 'new_password2']


# Manually set the order of fields so that "Current Password" comes first
# https://github.com/pennersr/django-allauth/issues/356#issuecomment-24758824
# Will no longer be necessary in django 1.8
ChangeOdinPasswordForm.base_fields = OrderedDict(
    (k, ChangeOdinPasswordForm.base_fields[k]) for k in ['current_password', 'new_password1', 'new_password2'])


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
        exclude = ['psu_uuid', ]


# Main MyInfo login form.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, label="Odin Username or PSU ID Number")
    password = forms.CharField(max_length=32, label="Password", widget=forms.PasswordInput())