from datetime import date

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from MyInfo.models import ContactInformation

from AccountPickup.forms import AccountClaimLoginForm, AcceptAUPForm, OdinNameForm, EmailAliasForm, ContactInformationWithOptOutForm
from AccountPickup.models import OAMStatusTracker

from lib.api_calls import truename_odin_names, truename_email_aliases, launch_provisioning_workflow, identity_from_psu_uuid

from brake.decorators import ratelimit

import logging
logger = logging.getLogger(__name__)

# The index of this module performs a non-CAS login to the AccountPickup system.
@ratelimit(block = True, rate='10/m')
@ratelimit(block = True, rate='50/h')
def index(request):
    error_message = ""
    form = AccountClaimLoginForm(request.POST or None)
        
    if form.is_valid():
        # For some reason they already have a session. Let's get rid of it and start fresh.
        if request.session is not None:
            request.session.flush()
            
        user = auth.authenticate(id_number=form.cleaned_data['id_number'],
                                 birth_date=form.cleaned_data['birth_date'],
                                 password=form.cleaned_data['auth_pass'],
                                 request=request)
        logger.info("Account claim login attempt with ID: {0}".format(form.cleaned_data['id_number']))
        if user is not None:
            #Identity is valid.
            auth.login(request, user)
            logger.info("Account claim login success with ID: {0}".format(form.cleaned_data['id_number']))
            
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        #If identity is invalid, prompt re-entry.
        error_message = "That identity was not found."
    
    return render(request, 'AccountPickup/index.html', {
        'form' : form,
        'error' : error_message,
    })
 
# Acceptable use policy.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def AUP(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    if oam_status.agree_aup is not None:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    form = AcceptAUPForm(request.POST or None)
        
    if form.is_valid():
        oam_status.agree_aup = date.today()
        oam_status.save()
        
        logger.info("service=myinfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " aup=true")
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/aup.html', {
        'form' : form,
    })
    
# Password reset information.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def contact_info(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    if oam_status.set_contact_info is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    # Build our password reset information form.
    (contact_info, _) = ContactInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    form = ContactInformationWithOptOutForm(request.POST or None, instance=contact_info)
    request.session['opt-out'] = False
    
    if form.is_valid():
        if form.cleaned_data['opt_out'] is True and form.cleaned_data['cell_phone'] is None and form.cleaned_data['alternate_email'] is None:
            request.session['opt-out'] = True
        else:
            request.session['opt-out'] = form.cleaned_data['opt_out']
            form.save()
        
            oam_status.set_contact_info = True
            oam_status.save()
        
        logger.info("service=myinfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " password_reset=true")
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/password_reset.html', {
        'form': form,
    })
    
# Select ODIN name
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def odinName(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    if oam_status.select_names is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    # Get possible odin names
    request.session['TRUENAME_USERNAMES'] = truename_odin_names(request.session['identity'])
    # Get possible email aliases
    request.session['TRUENAME_EMAILS'] = truename_email_aliases(request.session['identity'])
    
    # Build our forms with choices from truename.
    odinForm = OdinNameForm(enumerate(request.session['TRUENAME_USERNAMES']), request.POST or None)
    mailForm = EmailAliasForm(enumerate(request.session['TRUENAME_EMAILS']), request.POST or None)
    
    # Run both validations before the test so that short-circuiting does not bypass a validation.
    odin_valid = odinForm.is_valid()
    mail_valid = mailForm.is_valid()
        
    if odin_valid and mail_valid:
        logger.info("service=myinfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " odin_name=" + odinForm.cleaned_data['name'] + " email_alias=" + mailForm.cleaned_data['alias'])
        
        # Send the information to sailpoint to begin provisioning.
        odin_name = request.session['TRUENAME_USERNAMES'][int(odinForm.cleaned_data['name'])]
        email_alias = request.session['TRUENAME_EMAILS'][int(mailForm.cleaned_data['alias'])]
        launch_provisioning_workflow(request.session['identity'], odin_name, email_alias)
        
        oam_status.select_names = True
        oam_status.save()
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/odin_name.html', {
        'odin_form' : odinForm,
        'mail_form' : mailForm,
    })
    
# Pause and wait for provisioning to finish if necessary. This page uses AJAX calls to determine
# when it's safe to move on to setting a password.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def wait_for_provisioning(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    if oam_status.provisioned is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/wait_for_provisioning.html')

@login_required(login_url=reverse_lazy('AccountPickup:index'))
def provisioning_complete(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    if oam_status.select_names is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    oam_status.provisioned = True
    oam_status.save()
    
    # Because identity values may have changed due to SP Provisioning, update our identity.
    request.session['identity'] = identity_from_psu_uuid(request.session['identity']['PSU_UUID'])
    
    return HttpResponseRedirect(reverse('AccountPickup:next_step'))

@login_required(login_url=reverse_lazy('AccountPickup:index'))   
def oam_status_router(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    
    if oam_status.agree_aup is None:
        return HttpResponseRedirect(reverse('AccountPickup:aup'))
    
    elif oam_status.select_names is False:
        return HttpResponseRedirect(reverse('AccountPickup:odin'))
    
    # If they haven't set their contact_info and haven't opted out for the session, have them do that.
    elif oam_status.set_contact_info is False and (not "opt-out" in request.session or request.session("opt-out") == False):
        return HttpResponseRedirect(reverse('AccountPickup:contact_info'))
    
    elif oam_status.provisioned is False:
        return HttpResponseRedirect(reverse('AccountPickup:wait_for_provisioning'))
    
    # The identity should be expected to exist and be loaded into the session for any user past provisioning.
    
    # Only identities with PSU_PUBLISH == True should be directed to set their identity information.
    elif oam_status.set_directory is False and request.session['identity']['PSU_PUBLISH'] is True:
        return HttpResponseRedirect(reverse('MyInfo:set_directory', kwargs={'workflow_mode': True}))
    
    elif oam_status.set_password is False:
        return HttpResponseRedirect(reverse('MyInfo:set_password', kwargs={'workflow_mode': True}))
    
    else:
        # OAM has been completed. Dump them to MyInfo main page.
        return HttpResponseRedirect(reverse('MyInfo:set_password'))