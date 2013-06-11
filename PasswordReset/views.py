from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from PasswordReset.forms import request_reset_form, token_form
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from brake.decorators import ratelimit
from MyInfo.models import UserDataItem

import logging
logger = logging.getLogger(__name__)

@ratelimit(block = False, rate='5/m')
@ratelimit(block = True, rate='10/h')
def index(request):
    error_message = None
    reset_request = request_reset_form(request.POST or None)
    reset_token = token_form(None)
    email_response = False
    
    if getattr(request, 'limited', False):
        error_message = "Rate Limited"
    
    try:
        if reset_request.is_valid():
            if reset_request.cleaned_data['email'] != '':
                user_data = UserDataItem.objects.get(key_name='EXTERNAL_EMAIL_ADDRESS', key_valu=reset_request.cleaned_data['email'])
                email_response = True
            else:
                user_data = UserDataItem.objects.get(key_name='CELL_PHONE_NUMBER', key_valu=reset_request.cleaned_data['cell'])
    
            signer = TimestampSigner()
            token = signer.sign(user_data.psu_uuid)
            error_message = token
            
            if email_response == True:
                # TODO: Email the thingy.
                pass
            else:
                # TODO: Text the thingy.
                pass
            
    except (UserDataItem.DoesNotExist, UserDataItem.MultipleObjectsReturned):
        # Either we couldn't find it or we couldn't uniquely identify it.
        error_message = "We were unable to find an identity that matched your information."
    
    return render(request, 'PasswordReset/index.html', {'reset_request' : reset_request, 'reset_token' : reset_token, 'error' : error_message})

@ratelimit(block = False, rate='5/m')
@ratelimit(block = True, rate='10/h')
def reset(request, token=None):
    error_message = None
    signer = TimestampSigner()
    
    reset_token = token_form(request.POST or None)
    if reset_token.is_valid():
        token = reset_token.cleaned_data['token']
    
    try:
        # max_age is in seconds, so 1 hr.
        psu_uuid = signer.unsign(token, max_age=60*60)
        
        # Verify psu_uuid, authenticate user, redirect to "new student" version of MyInfo.
        user = auth.authenticate(psu_uuid = psu_uuid, request=request)
        
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('MyInfo:update'))
        
        logger.error("Password reset received a signed psu_uuid but could not authenticate for: {}".format(psu_uuid))
        error_message = "There was an internal error. Please contact the helpdesk for support."
    except SignatureExpired:
        udc_id = signer.unsign(token)
        # Too slow!
        logger.info("Attempted password reset after timeout for: {}".format(udc_id))
        error_message = "The password reset expired. Please try again."
    except BadSignature:
        logger.info("Attempted reset of invalid token: {}".format(token))
        error_message = "There was an internal error. Please contact the helpdesk for support."
    
    # Something went wrong, forward them back to the password reset link page.  
    if error_message is None:
        error_message = "There was an internal error. Please contact the helpdesk for support."
        logger.debug("Reached end of key signing attempt without an error message for token: {}".format(token))
    form = request_reset_form(request.POST or None)
    return render(request, 'PasswordReset/index.html', {'login_form' : form, 'error' : error_message})

