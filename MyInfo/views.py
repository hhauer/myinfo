# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy

from lib.api_calls import passwordConstraintsFromIdentity, identity_from_psu_uuid

from MyInfo.forms import formPasswordChange, formNewPassword, LoginForm, DirectoryInformationForm, ContactInformationForm
from MyInfo.models import DirectoryInformation, ContactInformation

from brake.decorators import ratelimit

import logging
logger = logging.getLogger(__name__)

@ratelimit(block = True, rate='10/m')
@ratelimit(block = True, rate='50/h')
def index(request):
    login_form = LoginForm(request.POST or None)
    error_message = ""
    
        
    if login_form.is_valid():
        # If for some reason they already have a session, let's get rid of it and start fresh.
        if request.session is not None:
            request.session.flush()
            
        user = auth.authenticate(username=login_form.cleaned_data['username'],
                                 password=login_form.cleaned_data['password'],
                                 request=request)
        logger.debug("OAM Login Attempt: {0}".format(login_form.cleaned_data['username']))
        
        if user is not None:
            #Identity is valid.
            auth.login(request, user)
            logger.info("service=myinfo login_username=" + login_form.cleaned_data['username'] + " success=true")
            
            # Head to the oam status router in case they have any unmet oam tasks.
            return HttpResponseRedirect(reverse("AccountPickup:oam_status_router"))
        
        #If identity is invalid, prompt re-entry.
        error_message = "That identity was not found."
    
    return render(request, 'MyInfo/index.html', {
        'form' : login_form,
        'error' : error_message,
    })
    
        
@login_required(login_url=reverse_lazy('MyInfo:index'))
def update_information(request, workflow_mode = False):
    # If the session has not yet opted-out of supernag set opt-out to false.
    if not "opt-out" in request.session:
        request.session["opt-out"] = False
        
    # Find out which auth backend we used, is this a new user or returning user?
    if request.session['_auth_user_backend'] == 'lib.backends.AccountPickupBackend':
        new_user = True
        passwordForm = formNewPassword(request.POST or None)
        
        # Because identity values may have changed due to SP Provisioning, update our identity.
        request.session['identity'] = identity_from_psu_uuid(request.session['identity']['PSU_UUID'])
    else:
        new_user = False
        passwordForm = formPasswordChange(request.POST or None)
        
    # Sets the default checked-state of the opt-out button.
    if request.session["opt-out"] is True:
        checked = 'checked'
    else:
        checked = ''
    
    if 'identity' not in request.session:
        logger.critical("No identity for user at MyInfo: {0}".format(request.session))
        return HttpResponseServerError('No identity information was available.')
    
    
    # Build our password reset information form.
    contact_info = ContactInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    contact_info_form = ContactInformationForm(instance=contact_info)
    
    # Are they an employee with information to update?
    if request.session['identity']['PSU_PUBLISH'] == True:
        directory_info, _ = DirectoryInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
        directory_info_form = DirectoryInformationForm(instance=directory_info)
    else:
        directory_info_form = None
        
    password_rules = passwordConstraintsFromIdentity(request.session['identity'])
    
    return render(request, 'MyInfo/update_info.html', {
    'identity' : request.session['identity'],
    'password_rules' : password_rules,
    'passwordForm' : passwordForm,
    'contact_info_form' : contact_info_form,
    'directory_info_form' : directory_info_form,
    'new_user' : new_user,
    'checked' : checked,
    })
    
@login_required(login_url=reverse_lazy('MyInfo:index'))
def set_password(request, workflow_mode = False):
    pass

@login_required(login_url=reverse_lazy('MyInfo:index'))
def set_directory(request, workflow_mode = False):
    pass

@login_required(login_url=reverse_lazy('MyInfo:index'))
def set_contact(request):
    pass