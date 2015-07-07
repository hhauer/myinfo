from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth

from lib.api_calls import password_reset_email, password_reset_sms, APIException

from PasswordReset.forms import ResetRequestForm, ResetTokenForm
from PasswordReset.models import TextMessageShortCode

from MyInfo.models import ContactInformation

from AccountPickup.models import OAMStatusTracker

from brake.decorators import ratelimit

import logging
logger = logging.getLogger(__name__)


@ratelimit(method='POST', rate='30/m')
@ratelimit(method='POST', rate='250/h')
def index(request):
    limited = getattr(request, 'limited', False)
    if limited:
        return HttpResponseRedirect(reverse('rate_limited'))

    error_message = None
    reset_request = ResetRequestForm(request.POST or None)
    email_response = False
    
    try:
        if reset_request.is_valid():
            if reset_request.cleaned_data['email'] != '':
                user_data = ContactInformation.objects.get(alternate_email=reset_request.cleaned_data['email'])
                email_response = True
            else:
                user_data = ContactInformation.objects.get(cell_phone=reset_request.cleaned_data['cell'])
    
            signer = TimestampSigner()
            token = signer.sign(user_data.psu_uuid)
            
            if email_response is True:
                r = password_reset_email(user_data.psu_uuid, user_data.alternate_email, token)

            else:
                short_code = TextMessageShortCode()
                short_code.token = token
                short_code.save()
                
                r = password_reset_sms(user_data.cell_phone, short_code.code)

            if r is not True:
                raise APIException("Reset code not sent. Email? " + str(email_response))

            logger.info(
                "service=myinfo page=passwordreset action=reset_request status=success email={0} cell={1}".format(
                    reset_request.cleaned_data['email'], reset_request.cleaned_data['cell']))
            return HttpResponseRedirect(reverse("PasswordReset:reset_notoken"))
            
    except (ContactInformation.DoesNotExist, ContactInformation.MultipleObjectsReturned) as e:
        # Either we couldn't find it or we couldn't uniquely identify it.
        if isinstance(e, ContactInformation.DoesNotExist):
            status = "id_not_found"
        else:
            status = "multiple_matches"
        logger.info(
            "service=myinfo page=passwordreset action=reset_request status={0} email={1} cell={2}".format(
                status, reset_request.cleaned_data['email'], reset_request.cleaned_data['cell']))

        error_message = ("We could not uniquely identify a user with this information. "
                         "Ensure this information is correct and please try again. "
                         "If you continue to have difficulty, contact the Helpdesk (503-725-4357) for assistance.")
    except APIException:

        logger.info(
            "service=myinfo page=passwordreset action=reset_request status=code_not_sent email={0} cell={1}".format(
                reset_request.cleaned_data['email'], reset_request.cleaned_data['cell']))

        error_message = "Sorry, we were unable to send a reset code. Please try again later."
    
    return render(request, 'PasswordReset/index.html', {'form': reset_request, 'error': error_message, })


@ratelimit(rate='30/m')
@ratelimit(rate='250/h')
def reset(request, token=None):
    limited = getattr(request, 'limited', False)
    if limited:
        return HttpResponseRedirect(reverse('rate_limited'))

    error_message = None
    signer = TimestampSigner()
        
    reset_token_form = ResetTokenForm(request.POST or None)
    
    # Token not passed through URL parameter.
    if token is None and reset_token_form.is_valid():
        token = reset_token_form.cleaned_data['token']

    if token is not None:
        encrypted_token = None
        # The token might be a short code. First try to look up a matching short code.
        try:
            short_code = TextMessageShortCode.objects.get(code=token)
            encrypted_token = short_code.token
        except TextMessageShortCode.DoesNotExist:
            encrypted_token = token

        try:
            # max_age is in seconds, so 1 hr.
            psu_uuid = signer.unsign(encrypted_token, max_age=60*60)
            
            # Verify psu_uuid, authenticate user, redirect to "new student" version of MyInfo.
            user = auth.authenticate(psu_uuid=psu_uuid, request=request)
            
            if user is not None:
                auth.login(request, user)

                # Now they need to reset their password.
                (oam_status, _) = OAMStatusTracker.objects.get_or_create(
                    psu_uuid=request.session['identity']['PSU_UUID'])
                oam_status.set_password = False
                oam_status.save()

                logger.info(
                    "service=myinfo page=passwordreset action=login status=success token={0} psu_uuid={1}".format(
                        token, user.get_username()))
                return HttpResponseRedirect(reverse('AccountPickup:next_step'))
            
            logger.error("service=myinfo psu_uuid={0} error=reset_authentication".format(psu_uuid))
            error_message = "There was an internal error. Please contact the Helpdesk (503-725-4357) for assistance."
        except SignatureExpired:
            udc_id = signer.unsign(token)
            # Too slow!
            logger.info("service=myinfo page=passwordreset action=login status=timeout token={0} psu_uuid={1}".format(
                token, udc_id))
            error_message = "The password reset expired. Please try again."
        except BadSignature:
            logger.info("service=myinfo page=passwordreset action=login status=invalid_token token={0}".format(token))
            error_message = "There was an internal error. Please contact the Helpdesk (503-725-4357) for assistance."
    
        # Something went wrong, forward them back to the password reset link page.  
        if error_message is None:
            error_message = "There was an internal error. Please contact the Helpdesk (503-725-4357) for assistance."
            logger.debug("Reached end of key signing attempt without an error message for token: {0}".format(token))

    return render(request, 'PasswordReset/verification.html', {'form': reset_token_form, 'error': error_message, })