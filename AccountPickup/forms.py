from django import forms

from lib.api_calls import set_email_alias, set_odin_username, APIException
from AccountPickup.models import OAMStatusTracker

import logging
logger = logging.getLogger(__name__)


class AccountClaimLoginForm(forms.Form):
    id_number = forms.CharField(min_length=9, max_length=9, label="ID Number")
    birth_date = forms.DateField(label="Birth Date (MM/DD/YYYY)")
    auth_pass = forms.CharField(label="Activation Code", widget=forms.PasswordInput())


class AcceptAUPForm(forms.Form):
    accepted = forms.BooleanField(label="I Accept")


# Must override __init__ to dynamically allocate choices for each user.
class OdinNameForm(forms.Form):
    def __init__(self, session, *args, **kwargs):
        super(OdinNameForm, self).__init__(*args, **kwargs)
        self.fields["name"] = forms.ChoiceField(choices=enumerate(session['TRUENAME_USERNAMES']), label="Odin Username")
        self.session = session

    def save(self):
        # Must save OAMStatus before API call, or it'll set provisioned back to false.
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        oam_status.select_odin_username = True
        oam_status.save(update_fields=['select_odin_username'])

        # Send the information to sailpoint to begin provisioning.
        name = self.session['TRUENAME_USERNAMES'][int(self.cleaned_data['name'])]
        status = set_odin_username(self.session['identity'], name)

        if status != "SUCCESS":  # API call to IIQ failed
            oam_status.select_odin_username = False
            oam_status.save(update_fields=['select_odin_username'])
            raise APIException("IIQ API call failed: Odin not set")

        self.session['identity']['ODIN_NAME'] = name
        self.session['identity']['EMAIL_ADDRESS'] = name + "@pdx.edu"
        self.session.modified = True  # Manually notify Django we modified a sub-object of the session.

        logger.info("service=myinfo psu_uuid=" + self.session['identity']['PSU_UUID'] + " odin_name=" + name)

        return self.session


class EmailAliasForm(forms.Form):
    def __init__(self, session, *args, **kwargs):
        super(EmailAliasForm, self).__init__(*args, **kwargs)
        self.fields["alias"] = forms.ChoiceField(
            choices=enumerate(session['TRUENAME_EMAILS']), label="Email Alias")
        self.session = session

    def save(self):
        alias = self.session['TRUENAME_EMAILS'][int(self.cleaned_data['alias'])]
        logger.debug("Email alias value: " + alias)

        if alias is not None and alias != 'None':
            result = set_email_alias(self.session['identity'], alias)
            if result is not True:
                # API call failed
                raise APIException("API call to set_email_alias did not return success.")

            self.session['identity']['EMAIL_ALIAS'] = alias
            self.session.modified = True  # Manually notify Django we modified a sub-object of the session.

            logger.info("service=myinfo psu_uuid={0} email_alias={1}".format(
                self.session['identity']['PSU_UUID'], alias))

        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        oam_status.select_email_alias = True
        oam_status.save(update_fields=['select_email_alias'])

        return self.session