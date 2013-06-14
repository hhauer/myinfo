# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from MyInfo.forms import formPasswordChange, formNewPassword, formExternalContactInformation, formPSUEmployee, expired_password_login_form
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from PSU_MyInfo.api_calls import identity_from_cas, passwordConstraintsFromIdentity, identity_from_psu_uuid
from MyInfo.util_functions import contact_initial, directory_initial
from django.contrib import auth
from django.core.urlresolvers import reverse
from brake.decorators import ratelimit

from MyInfo.forms import ReCaptchaForm

import logging
logger = logging.getLogger(__name__)

@ratelimit(block = False, rate='5/m')
@ratelimit(block = True, rate='10/h')
def index(request):
    captcha = None
    form = expired_password_login_form(request.POST or None)
    error_message = ""
    
    if getattr(request, 'limited', False):
        captcha = ReCaptchaForm(request.POST or None)
        
    if form.is_valid() and (captcha is None or captcha.is_valid()):
        # For some reason they already have a session. Let's get rid of it and start fresh.
        if request.session is not None:
            request.session.flush()
            
        user = auth.authenticate(odin_username=form.cleaned_data['odin_username'],
                                 password=form.cleaned_data['password'],
                                 request=request)
        logger.info("Expired Password login attempt for Odin Username: ".format(form.cleaned_data['odin_username']))
        if user is not None:
            #Identity is valid.
            auth.login(request, user)
            
            logger.info("Expired Password login success for Odin Username: ".format(form.cleaned_data['odin_username']))
            
            return HttpResponseRedirect(reverse("MyInfo:update"))
        #If identity is invalid, prompt re-entry.
        error_message = "That identity was not found."
    
    return render(request, 'MyInfo/index.html', {
        'form' : form,
        'error' : error_message,
        'captcha' : captcha,
    })
    
        
@login_required(login_url='/accounts/login/')
def update_information(request):
    # If the session has not yet opted-out of supernag set opt-out to false.
    if not "opt-out" in request.session:
        request.session["opt-out"] = False
        
    # Find out which auth backend we used, is this a new user or returning user?
    if request.session['_auth_user_backend'] == 'django_cas.backends.CASBackend':
        newStudent = False
        passwordForm = formPasswordChange(request.POST or None)
    else:
        newStudent = True
        passwordForm = formNewPassword(request.POST or None)
    
    # Sets the default checked-state of the opt-out button.
    if request.session["opt-out"] is True:
        checked = 'checked'
    else:
        checked = ''
    
    if 'identity' not in request.session:
        logger.critical("No identity for user at MyInfo: {}".format(request.session))
        return HttpResponseServerError('No identity information was available.')
    
    # Refresh our identity.
    request.session['identity'] = identity_from_psu_uuid(request.session['identity']['PSU_UUID'])

    # Build our extended information form.
    contactForm = formExternalContactInformation(request.POST or None, initial=contact_initial(request))
    
    # Are they an employee with information to update?
    if True: #TODO: Stubbed
        psuEmployeeForm = formPSUEmployee(request.POST or None, initial=directory_initial(request.session['identity']['PSU_UUID']))
    else:
        psuEmployeeForm = None
        
    if contactForm.is_valid() and passwordForm.is_valid() and psuEmployeeForm.is_valid():
        #Do stuff with the forms.
        
        return HttpResponse('Valid forms detected.')
    else:
        password_rules = passwordConstraintsFromIdentity(request.session['identity'])
        
        return render(request, 'MyInfo/update_info.html', {
        'identity' : request.session['identity'],
        'password_rules' : password_rules,
        'passwordForm' : passwordForm,
        'contactForm' : contactForm,
        'PSUEmployeeForm' : psuEmployeeForm,
        'newStudent' : newStudent,
        'checked' : checked,
        })