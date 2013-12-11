from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth

from lib.api_calls import password_reset_email, password_reset_sms

from PasswordReset.forms import ResetRequestForm, ResetTokenForm
from PasswordReset.models import TextMessageShortCode

from MyInfo.forms import ReCaptchaForm
from MyInfo.models import ContactInformation

from brake.decorators import ratelimit

import logging
logger = logging.getLogger(__name__)

@ratelimit(block = False, rate='5/m')
@ratelimit(block = True, rate='10/h')
def index(request):
    error_message = None
    reset_request = ResetRequestForm(request.POST or None)
    email_response = False
    captcha = None
    
    if getattr(request, 'limited', False):
        captcha = ReCaptchaForm(request.POST or None)
    
    try:
        if reset_request.is_valid() and (captcha is None or captcha.is_valid()):
            if reset_request.cleaned_data['email'] != '':
                user_data = ContactInformation.objects.get(alternate_email=reset_request.cleaned_data['email'])
                email_response = True
            else:
                user_data = ContactInformation.objects.get(cell_phone=reset_request.cleaned_data['cell'])
    
            signer = TimestampSigner()
            token = signer.sign(user_data.psu_uuid)
            
            if email_response == True:
                password_reset_email(user_data.psu_uuid, user_data.alternate_email, token)
            else:
                shortcode = TextMessageShortCode()
                shortcode.token = token
                shortcode.save()
                
                password_reset_sms(user_data.cell_phone, shortcode.code)
            
            return HttpResponseRedirect(reverse("PasswordReset:reset_notoken"))
            
    except (ContactInformation.DoesNotExist, ContactInformation.MultipleObjectsReturned):
        # Either we couldn't find it or we couldn't uniquely identify it.
        logger.info("service=myinfo email=" + reset_request.cleaned_data['email'] + " cell=" + reset_request.cleaned_data['cell'] + "error = \"Unable to identify.\"")
        error_message = "We were unable to find an identity that matched your information."
    
    return render(request, 'PasswordReset/index.html', {'reset_request' : reset_request, 'error' : error_message, 'captcha' : captcha,})

@ratelimit(block = False, rate='5/m')
@ratelimit(block = True, rate='10/h')
def reset(request, token=None):
    error_message = None
    signer = TimestampSigner()
    captcha = None
    
    if getattr(request, 'limited', False):
        captcha = ReCaptchaForm(request.POST or None)
        
    reset_token_form = ResetTokenForm(request.POST or None)
    
    # Token not passed through URL parameter.
    if token is None and reset_token_form.is_valid():
        token = reset_token_form.cleaned_data['token']
    
    
    if token is not None and (captcha is None or captcha.is_valid()):
        encrypted_token = None
        # The token might be a shortcode. First try to look up a matching shortcode.
        try:
            shortcode = TextMessageShortCode.objects.get(code=token)
            encrypted_token = shortcode.token
        except TextMessageShortCode.DoesNotExist:
            encrypted_token = token
            
        try:
            # max_age is in seconds, so 1 hr.
            psu_uuid = signer.unsign(encrypted_token, max_age=60*60)
            
            # Verify psu_uuid, authenticate user, redirect to "new student" version of MyInfo.
            user = auth.authenticate(psu_uuid = psu_uuid, request=request)
            
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('AccountPickup:oam_status_router'))
            
            logger.error("service=myinfo psu_uuid={0} error=\"Password token decrypted succesfully but unable to authenticate.\"".format(psu_uuid))
            error_message = "There was an internal error. Please contact the helpdesk for support."
        except SignatureExpired:
            udc_id = signer.unsign(token)
            # Too slow!
            logger.info("service=myinfo psu_uuid={0} error=password_timeout".format(udc_id))
            error_message = "The password reset expired. Please try again."
        except BadSignature:
            logger.info("service=myinfo token={0} error=\"An invalid reset token was passed to OAM PasswordReset\"")
            error_message = "There was an internal error. Please contact the helpdesk for support."
    
        # Something went wrong, forward them back to the password reset link page.  
        if error_message is None:
            error_message = "There was an internal error. Please contact the helpdesk for support."
            logger.debug("Reached end of key signing attempt without an error message for token: {0}".format(token))

    return render(request, 'PasswordReset/reset.html', {'reset_token_form' : reset_token_form, 'error' : error_message, 'reset_captcha' : captcha,})

