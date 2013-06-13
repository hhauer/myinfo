# Create your views here.
# http://docs.python.org/2/library/json.html

from django.shortcuts import render
from django.http import HttpResponseRedirect
from AccountPickup.forms import accountClaimLogin, acceptAUP, pickOdinName, EmailAliasForm, password_reset_optout_form
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from brake.decorators import ratelimit

from MyInfo.models import UserDataItem

import logging
logger = logging.getLogger(__name__)

anchor = {
    "AccountPickup:AUP" : "#aup",
    "AccountPickup:ODIN" : "#odin",
    "AccountPickup:PasswordReset" : "#reset",
}

# The index of this module performs a non-CAS login to the AccountPickup system.
#@ratelimit(block = False, rate='5/m')
#@ratelimit(block = True, rate='10/h')
def index(request):
    error_message = ""
    form = accountClaimLogin(request.POST or None)
        
    if form.is_valid():
        # For some reason they already have a session. Let's get rid of it and start fresh.
        if request.session is not None:
            request.session.flush()
            
        user = auth.authenticate(id_number=form.cleaned_data['id_number'],
                                 birth_date=form.cleaned_data['birth_date'],
                                 password=form.cleaned_data['auth_pass'],
                                 request=request)
        logger.info("Account claim login attempt with ID: {}".format(form.cleaned_data['id_number']))
        if user is not None:
            #Identity is valid.
            auth.login(request, user)
            logger.info("Account claim login success with ID: {}".format(form.cleaned_data['id_number']))
            
            # Where in the process should we be?
            (go_next, _) = UserDataItem.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'], key_name='MYINFO_PICKUP_STATE', 
                                                           defaults={'key_valu' : 'AccountPickup:AUP'})
            request.session['NEXT'] = go_next.key_valu
            return HttpResponseRedirect(reverse(go_next.key_valu) + anchor[go_next.key_valu])
        #If identity is invalid, prompt re-entry.
        error_message = "That identity was not found."
    
    return render(request, 'AccountPickup/index.html', {
        'form' : form,
        'error' : error_message,
    })
 
# Acceptable use policy.
@login_required(login_url='/AccountPickup/')
def AUP(request):
    if request.session['NEXT'] != 'AccountPickup:AUP':
        return HttpResponseRedirect(reverse(request.session['NEXT']) + anchor[request.session['NEXT']])
    
    form = acceptAUP(request.POST or None)
        
    if form.is_valid():
        # c is whether or not the object was created, but here we don't care so it is silently discarded.
        (reg_aup, _) = UserDataItem.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'], key_name='ACCEPT_USER_POLICY')
        reg_aup.key_valu = 'True'
        reg_aup.save()
        
        # Move on to the odin name picker.
        logger.debug("Valid response to AUP received.")
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID'], 
                                    key_name ='MYINFO_PICKUP_STATE').update(key_valu = 'AccountPickup:PasswordReset')
        request.session['NEXT'] = 'AccountPickup:PasswordReset'
        return HttpResponseRedirect(reverse('AccountPickup:PasswordReset') + anchor[request.session['NEXT']])
    
    return render(request, 'AccountPickup/aup.html', {
        'form' : form,
    })
    
# Password reset information.
@login_required(login_url='/AccountPickup/')
def password_reset(request):
    if request.session['NEXT'] != 'AccountPickup:PasswordReset':
        return HttpResponseRedirect(reverse(request.session['NEXT']) + anchor[request.session['NEXT']])
    
    reset_form = password_reset_optout_form(request.POST or None)
    
    request.session['opt-out'] = False
    
    if reset_form.is_valid() and reset_form.cleaned_data['opt_out'] is True:
        request.session['opt-out'] = True
    
    if reset_form.is_valid():
        (email, _) = UserDataItem.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'], key_name='EXTERNAL_EMAIL_ADDRESS', defaults={'key_valu' : ''})
        (cell, _) = UserDataItem.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'], key_name='CELL_PHONE_NUMBER', defaults={'key_valu' : ''})
        (carr, _) = UserDataItem.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'], key_name='CELL_PHONE_CARRIER', defaults={'key_valu' : ''})
        
        email.key_valu = reset_form.cleaned_data['alternate_email']
        email.save()
        
        cell.key_valu = reset_form.cleaned_data['cell_number']
        cell.save()
        
        carr.key_valu = reset_form.cleaned_data['cell_carrier']
        carr.save()
        
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID'], 
                                    key_name ='MYINFO_PICKUP_STATE').update(key_valu = 'AccountPickup:ODIN')
        request.session['NEXT'] = 'AccountPickup:ODIN'
        return HttpResponseRedirect(reverse('AccountPickup:ODIN') + anchor[request.session['NEXT']])
    
    return render(request, 'AccountPickup/password_reset.html', {
        'form': reset_form,
    })
    
# Select ODIN name
@login_required(login_url='/AccountPickup/')
def odinName(request):
    if request.session['NEXT'] != 'AccountPickup:ODIN':
        return HttpResponseRedirect(reverse(request.session['NEXT']) + anchor[request.session['NEXT']])
    
    # Pass in the session to the odinForm so that it can get appropriate name options.
    odinForm = pickOdinName(request.session, request.POST or None)
    mailForm = EmailAliasForm(request.session, request.POST or None)
    
    # These forms are processed via an ajax submit to the endpoint provision_new_user
    
    return render(request, 'AccountPickup/odin_name.html', {
        'odin_form' : odinForm,
        'mail_form' : mailForm,
    })