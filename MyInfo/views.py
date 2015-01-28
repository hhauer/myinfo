import datetime

from django.shortcuts import render
from django.http import HttpResponseServerError, HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import Error

from lib.api_calls import change_password

from MyInfo.forms import formPasswordChange, formNewPassword, LoginForm, DirectoryInformationForm, \
    ContactInformationForm
from MyInfo.models import DirectoryInformation, ContactInformation, MaintenanceNotice, Department

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

    login_form = LoginForm(request.POST or None)
    error_message = ""

    if login_form.is_valid():
        # If for some reason they already have a session, let's get rid of it and start fresh.
        if request.session is not None:
            request.session.flush()

        logger.debug("OAM Login Attempt: {0}".format(login_form.cleaned_data['username']))

        user = auth.authenticate(username=login_form.cleaned_data['username'],
                                 password=login_form.cleaned_data['password'],
                                 request=request)

        if user is not None:
            # Identity is valid.
            auth.login(request, user)
            logger.info("service=myinfo login_username=" + login_form.cleaned_data['username'] + " success=true")

            # Head to the oam status router in case they have any unmet oam tasks.
            return HttpResponseRedirect(reverse("AccountPickup:next_step"))

        # If identity is invalid, prompt re-entry.
        error_message = "That identity was not found."

        # logger.debug("Error during login with username: {0} and password: {1}".format(
        #   login_form.cleaned_data["username"], login_form.cleaned_data["password"]))

    # Determine whether or not to render a maintenance notice.
    notices = MaintenanceNotice.objects.filter(
        start_display__lte=datetime.datetime.now()
    ).filter(
        end_display__gte=datetime.datetime.now()
    )

    return render(request, 'MyInfo/index.html', {
        'form': login_form,
        'error': error_message,
        'notices': notices,
    })


# Present the user with a list of appropriate actions for them to be able to take.
# This serves as a navigation menu.
@login_required(login_url=reverse_lazy('index'))
def pick_action(request):
    return render(request, 'MyInfo/pick_action.html', {
        'identity': request.session['identity'],
        'allow_cancel': request.session['ALLOW_CANCEL'],
    })


@login_required(login_url=reverse_lazy('index'))
def set_password(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])

    if oam_status.set_password is True:
        form = formPasswordChange(request.POST or None)
    else:
        form = formNewPassword(request.POST or None)

    if 'identity' not in request.session:  # pragma: no cover
        # Shouldn't happen, the above get_or_create would error out first.
        logger.critical("service=myinfo error=no_identity_at_password session={0}".format(request.session))
        return HttpResponseServerError('No identity information was available.')

    success = False
    message = None
    if form.is_valid():
        if oam_status.set_password is True:
            current_password = form.cleaned_data['currentPassword']
        else:
            current_password = None

        (success, message) = change_password(request.session['identity'],
                                             form.cleaned_data['newPassword'],
                                             current_password)

        if oam_status.set_password is False and success is True:
            oam_status.set_password = True
            oam_status.save()

        if success is True:
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    # Consider rendering when the password expires. Eventually.
    return render(request, 'MyInfo/set_password.html', {
        'identity': request.session['identity'],
        'form': form,
        'success': success,
        'error': message,
        'allow_cancel': request.session['ALLOW_CANCEL'],
    })


@login_required(login_url=reverse_lazy('index'))
def set_directory(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])

    # Are they an employee with information to update?
    if request.session['identity']['PSU_PUBLISH'] is True:
        (directory_info, _) = DirectoryInformation.objects.get_or_create(
            psu_uuid=request.session['identity']['PSU_UUID'])
        directory_info_form = DirectoryInformationForm(request.POST or None, instance=directory_info)
    else:
        oam_status.set_directory = True
        oam_status.save()
        return HttpResponseRedirect(reverse("AccountPickup:next_step"))  # Shouldn't be here.

    if directory_info_form.is_valid():
        directory_info_form.save()
        if oam_status.set_directory is False:  # pragma: no branch
            oam_status.set_directory = True
            oam_status.save()

        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    return render(request, 'MyInfo/set_directory.html', {
        'identity': request.session['identity'],
        'form': directory_info_form,
        'allow_cancel': request.session['ALLOW_CANCEL'],
    })


@login_required(login_url=reverse_lazy('index'))
def set_contact(request):
    # We don't check OAMStatusTracker because if they don't have contact info set they will be sent to the
    # AccountPickup version of this page. This is just for changing existing contact info.

    # Build our password reset information form.
    (contact_info, _) = ContactInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    contact_info_form = ContactInformationForm(request.POST or None, instance=contact_info)

    if contact_info_form.is_valid():
        # First check to see if they removed all their contact info.
        # Currently this shouldn't happen, since the underlying form rejects that state in validation.
        if contact_info_form.cleaned_data['cell_phone'] is None and contact_info_form.cleaned_data[
                'alternate_email'] is None:  # pragma: no cover
            (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
            oam_status.set_contact_info = False
            oam_status.save()

        contact_info_form.save()

        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    return render(request, 'MyInfo/set_contact.html', {
        'identity': request.session['identity'],
        'form': contact_info_form,
        'allow_cancel': request.session['ALLOW_CANCEL'],
    })


@login_required(login_url=reverse_lazy('index'))
def welcome_landing(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    oam_status.welcome_displayed = True
    oam_status.save()

    identity = request.session['identity']

    # Kill the session. They are now done.
    request.session.flush()

    return render(request, 'MyInfo/welcome_landing.html', {
        'identity': identity,
    })


# Handle an F5 ping.
def ping(request):
    # Can we get something from the database?
    try:
        _ = Department.objects.all()[0]
        return HttpResponse("Success")
    except (Error, IndexError):
        return HttpResponse("Database not available!")
