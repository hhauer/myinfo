from collections import OrderedDict
from django import forms

from MyInfo.models import DirectoryInformation, ContactInformation
from AccountPickup.models import OAMStatusTracker
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

            if old_pw is None:
                action = "set_password"
            else:
                action = "change_password"

            if status is False:
                # Log failure
                error_text = "\"[" + ",".join(errors) + "]\""
                logger.info("service=myinfo page=myinfo action={0} status={1} psu_uuid={2}".format(
                            action, error_text, self.user.get_username()))
                raise forms.ValidationError([forms.ValidationError(error) for error in errors])
            else:
                # Password is not stored in user object, but new hash is needed for auth purposes
                self.user.set_unusable_password()
                self.user.save(update_fields=['password'])
                logger.info("service=myinfo page=myinfo action={0} status=success psu_uuid={1}".format(
                            action, self.user.get_username()))

    def save(self, commit=True):
        # Save status
        psu_uuid = self.user.get_username()
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=psu_uuid)
        if oam_status.set_password is False:
            oam_status.set_password = True
            oam_status.save(update_fields=['set_password'])
        return self.user


class ChangeOdinPasswordForm(SetOdinPasswordForm):
    current_password = forms.CharField(
        min_length=8, max_length=30, widget=forms.PasswordInput, label="Current password")

    # Field ordering. Not valid code until future django changes are implemented
    # field_order = ['current_password', 'new_password1', 'new_password2']


# Manually set the order of fields so that "Current Password" comes first
# https://github.com/pennersr/django-allauth/issues/356#issuecomment-24758824
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

    def __init__(self, psu_uuid, *args, **kwargs):
        super(DirectoryInformationForm, self).__init__(*args, **kwargs)
        self.psu_uuid = psu_uuid

    def save(self, commit=True):
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.psu_uuid)
        if oam_status.set_directory is False:
            oam_status.set_directory = True
            oam_status.save(update_fields=['set_directory'])
        logger.info("service=myinfo psu_uuid={0} directory_set=true".format(self.psu_uuid))

        return super(DirectoryInformationForm, self).save(commit=commit)


# Main MyInfo login form.
class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, label="Odin Username or PSU ID Number")
    password = forms.CharField(max_length=32, label="Password", widget=forms.PasswordInput())
