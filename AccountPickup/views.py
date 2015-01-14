from datetime import date, timedelta

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from MyInfo.models import ContactInformation
from MyInfo.forms import ContactInformationForm

from AccountPickup.forms import AccountClaimLoginForm, AcceptAUPForm, OdinNameForm, EmailAliasForm
from AccountPickup.models import OAMStatusTracker

from lib.api_calls import truename_odin_names, truename_email_aliases, set_odin_username, identity_from_psu_uuid, set_email_alias, \
    get_provisioning_status

from brake.decorators import ratelimit

import logging
logger = logging.getLogger(__name__)


# The index of this module performs a non-CAS login to the AccountPickup system.
@ratelimit(block=True, rate='10/m')
@ratelimit(block=True, rate='50/h')
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
            # Identity is valid.
            auth.login(request, user)
            logger.info("Account claim login success with ID: {0}".format(form.cleaned_data['id_number']))
            
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        # If identity is invalid, prompt re-entry.
        error_message = "That identity was not found."
    
    return render(request, 'AccountPickup/index.html', {
        'form': form,
        'error': error_message,
    })


# Acceptable use policy.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def AUP(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.agree_aup is not None or oam_status.agree_aup + timedelta(weeks=26) < date.today():
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    form = AcceptAUPForm(request.POST or None)
        
    if form.is_valid():
        oam_status.agree_aup = date.today()
        oam_status.save()
        
        logger.info("service=MyInfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " aup=true")
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/aup.html', {
        'identity': request.session['identity'],
        'form': form,
    })


# Password reset information.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def contact_info(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.set_contact_info is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    # Build our password reset information form.
    (_contact_info, _) = ContactInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    contact_form = ContactInformationForm(request.POST or None, instance=_contact_info)
    
    # Did they provide valid contact information, if so we send them along.
    if contact_form.is_valid():
        contact_form.save()
        
        oam_status.set_contact_info = True
        oam_status.save()
        
        logger.info("service=MyInfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " password_reset=true")
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    elif request.method == 'POST':
        logger.debug(_contact_info)
        logger.debug(request.POST)
    
    return render(request, 'AccountPickup/contact_info.html', {
        'identity': request.session['identity'],
        'form': contact_form,
    })


# Select ODIN name
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def odinName(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.select_odin_username is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    # Get possible odin names
    if 'TRUENAME_USERNAMES' not in request.session:
        request.session['TRUENAME_USERNAMES'] = truename_odin_names(request.session['identity'])
        # If truename server is not responding, don't give user empty list
        if len(request.session['TRUENAME_USERNAMES']) == 0:
            raise Exception("Truename API call failed")

    # Build our forms with choices from truename.
    odin_form = OdinNameForm(enumerate(request.session['TRUENAME_USERNAMES']), request.POST or None)
        
    if odin_form.is_valid():
        # Must save OAMStatus before API call, or it'll set provisioned back to false.
        oam_status.select_odin_username = True
        oam_status.save()

        # Send the information to sailpoint to begin provisioning.
        odin_name = request.session['TRUENAME_USERNAMES'][int(odin_form.cleaned_data['name'])]
        r = set_odin_username(request.session['identity'], odin_name)
        if r != "SUCCESS":
            # API call to IIQ failed
            oam_status.select_odin_username = False
            oam_status.save()
            raise Exception("IIQ API call failed")

        request.session['identity']['ODIN_NAME'] = odin_name
        request.session['identity']['EMAIL_ADDRESS'] = odin_name + "@pdx.edu"
        request.session.modified = True  # Manually notify Django we modified a sub-object of the session.
        
        logger.info("service=MyInfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " odin_name=" + odin_name)

        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/odin_name.html', {
        'identity': request.session['identity'],
        'odin_form': odin_form,
    })


# Select Preferred email.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def email_alias(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.select_email_alias is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    # Get possible email aliases
    if 'TRUENAME_EMAILS' not in request.session:
        request.session['TRUENAME_EMAILS'] = truename_email_aliases(request.session['identity'])

        if len(request.session['TRUENAME_EMAILS']) == 0:
            # Truename down, don't offer empty list
            raise Exception("Truename API call failed")

        # Prepend a "None" option at the start of the emails.
        request.session['TRUENAME_EMAILS'].insert(0, 'None')

    # Build our forms with choices from truename.
    mail_form = EmailAliasForm(enumerate(request.session['TRUENAME_EMAILS']), request.POST or None)

    if mail_form.is_valid():
        # Send the information to sailpoint to begin provisioning.
        _email_alias = request.session['TRUENAME_EMAILS'][int(mail_form.cleaned_data['alias'])]
        logger.debug("Email alias value: " + _email_alias)

        if _email_alias is not None and _email_alias != 'None':
            r = set_email_alias(request.session['identity'], _email_alias)
            if r != "SUCCESS":
                # API call failed
                raise Exception("IIQ API call failed")

            request.session['identity']['EMAIL_ALIAS'] = _email_alias
            request.session.modified = True  # Manually notify Django we modified a sub-object of the session.

            logger.info(
                "service=MyInfo psu_uuid=" + request.session['identity']['PSU_UUID'] + " email_alias=" + _email_alias)

        oam_status.select_email_alias = True
        oam_status.save()
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    return render(request, 'AccountPickup/email_alias.html', {
        'identity': request.session['identity'],
        'mail_form': mail_form,
    })


# Pause and wait for provisioning to finish if necessary. This page uses AJAX calls to determine
# when it's safe to move on to setting a password.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def wait_for_provisioning(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.provisioned is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    
    return render(request, 'AccountPickup/wait_for_provisioning.html', {
        'identity': request.session['identity'],
    })


# Deprecated view? oam_status doesn't seem to have a 'select_names'
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def provisioning_complete(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.select_names is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    oam_status.provisioned = True
    oam_status.save()

    # Because identity values may have changed due to SP Provisioning, update our identity.
    request.session['identity'] = identity_from_psu_uuid(request.session['identity']['PSU_UUID'])

    return HttpResponseRedirect(reverse('AccountPickup:next_step'))


@login_required(login_url=reverse_lazy('AccountPickup:index'))   
def oam_status_router(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    request.session['ALLOW_CANCEL']=False

    if 'CHECKED_IIQ' not in request.session:
        provision_status = get_provisioning_status(request.session['identity']['PSU_UUID'])

        if len(provision_status) == 0:
            raise Exception("IIQ API call failed")

        # If they've already been through MyInfo, provisioned will be true and we don't want to pester them
        # a second time to pick an alias if previously they selected "none."
        if oam_status.provisioned is False:
            oam_status.select_email_alias = provision_status["ALIAS_SELECTED"]

        oam_status.provisioned = provision_status["PROVISIONED"]
        oam_status.welcome_displayed = provision_status["WELCOMED"]
        oam_status.select_odin_username = provision_status["ODIN_SELECTED"]

        oam_status.save()
        request.session['CHECKED_IIQ'] = True

    # They should be asked to agree every 6mo.
    if oam_status.agree_aup is None or oam_status.agree_aup + timedelta(weeks=26) < date.today():
        return HttpResponseRedirect(reverse('AccountPickup:aup'))
    
    elif oam_status.select_odin_username is False:
        return HttpResponseRedirect(reverse('AccountPickup:odin'))

    elif oam_status.select_email_alias is False:
        return HttpResponseRedirect(reverse('AccountPickup:alias'))
    
    # If they haven't set their contact_info and haven't opted out for the session, have them do that.
    elif oam_status.set_contact_info is False:
        return HttpResponseRedirect(reverse('AccountPickup:contact_info'))
    
    elif oam_status.provisioned is False:
        return HttpResponseRedirect(reverse('AccountPickup:wait_for_provisioning'))
    
    # Only identities with PSU_PUBLISH == True should be directed to set their identity information.
    elif oam_status.set_directory is False and request.session['identity']['PSU_PUBLISH'] is True:
        return HttpResponseRedirect(reverse('MyInfo:set_directory'))
    
    elif oam_status.set_password is False:
        return HttpResponseRedirect(reverse('MyInfo:set_password'))
    
    elif oam_status.welcome_displayed is False:
        return HttpResponseRedirect(reverse('MyInfo:welcome_landing'))
    
    else:
        request.session['ALLOW_CANCEL']= True
        # OAM has been completed. Dump them to MyInfo main page.
        return HttpResponseRedirect(reverse('MyInfo:pick_action'))