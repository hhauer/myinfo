# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy

from lib.api_calls import change_password

from MyInfo.forms import formPasswordChange, formNewPassword, LoginForm, DirectoryInformationForm, ContactInformationForm
from MyInfo.models import DirectoryInformation, ContactInformation

from AccountPickup.models import OAMStatusTracker

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
def set_password(request, workflow_mode = False):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    
    if oam_status.set_password is True and workflow_mode is True:
        # This was the last step for them if workflow_mode is true. TODO: Forward to landing page.
        return
    elif workflow_mode is True:
        form = formNewPassword(request.POST or None)
    else:
        form = formPasswordChange(request.POST or None)
        
    if 'identity' not in request.session:
        logger.critical("service=myinfo error=\"No identity information available at set password. Aborting.\" session=\"{0}\"".format(request.session))
        return HttpResponseServerError('No identity information was available.')
    
    success = False
    message = None
    if form.is_valid():
        if workflow_mode is True:
            (success, message) = change_password(request.session['identity'], form.cleaned_data['newPassword'], None)
            oam_status.set_password = True
            oam_status.save()
            
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        else:
            (success, message) = change_password(request.session['identity'], form.cleaned_data['newPassword'], form.cleaned_data['currentPassword'])
    
    return render(request, 'MyInfo/set_password.html', {
        'identity' : request.session['identity'],
        'form': form,
        'success': success,
        'message': message,
        'workflow': workflow_mode,
    })

@login_required(login_url=reverse_lazy('MyInfo:index'))
def set_directory(request, workflow_mode = False):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    
    if oam_status.set_directory is True and workflow_mode is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    # Are they an employee with information to update?
    if request.session['identity']['PSU_PUBLISH'] == True:
        directory_info, _ = DirectoryInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
        directory_info_form = DirectoryInformationForm(instance=directory_info, request.POST or None)
    else:
        return HttpResponseRedirect(reverse("AccountPickup:next_step")) # Shouldn't be here.
    
    if directory_info_form.is_valid():
        directory_info_form.save()
        if workflow_mode is True:
            oam_status.set_directory = True
            oam_status.save()
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        
    return render(request, 'MyInfo/set_directory.html', {
        'identity': request.session['identity'],
        'form': directory_info_form,
        'workflow': workflow_mode,
    })
    
    

@login_required(login_url=reverse_lazy('MyInfo:index'))
def set_contact(request):
    # We don't check OAMStatusTracker because if they don't have contact info set they will be sent to the AccountPickup
    # version of this page. This is just for changing existing contact info.
    
    # Build our password reset information form.
    contact_info = ContactInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    contact_info_form = ContactInformationForm(instance=contact_info, request.POST or None)
    
    if contact_info_form.is_valid():
        # First check to see if they removed all their contact info.
        if contact_info_form.cleaned_data['cell_phone'] is None and contact_info_form.cleaned_data['alternate_email'] is None:
            (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
            oam_status.set_contact_info = False
            oam_status.save()
        
        contact_info_form.save()
        
    return render(request, 'MyInfo/set_contact.html', {
        'identity': request.session['identity'],
        'form': contact_info_form,
    })