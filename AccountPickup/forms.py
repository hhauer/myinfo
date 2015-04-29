from django import forms

from lib.api_calls import set_email_alias, APIException
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
    def __init__(self, names, *args, **kwargs):
        super(OdinNameForm, self).__init__(*args, **kwargs)
        self.fields["name"] = forms.ChoiceField(choices=names, label="Odin Username")


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