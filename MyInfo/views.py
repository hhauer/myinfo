import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import Error
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from MyInfo.forms import ChangeOdinPasswordForm, SetOdinPasswordForm, LoginForm, DirectoryInformationForm, \
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
        if request.session is not None:  # pragma: no branch
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
        error_message = ("Username and/or Password not recognized. "
                         "Ensure this information is correct and please try again. "
                         "If you continue to have difficulty, contact the Helpdesk (503-725-4357) for assistance.")


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


# Replaced with class-based view
# # Present the user with a list of appropriate actions for them to be able to take.
# # This serves as a navigation menu.
# @login_required(login_url=reverse_lazy('index'))
# def pick_action(request):
# return render(request, 'MyInfo/pick_action.html', {
#         'identity': request.session['identity'],
#         'allow_cancel': request.session['ALLOW_CANCEL'],
#     })


class PickActionView(TemplateView):
    template_name = "MyInfo/pick_action.html"

    @method_decorator(login_required(login_url=reverse_lazy('index')))
    def dispatch(self, request, *args, **kwargs):
        return super(PickActionView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PickActionView, self).get_context_data(**kwargs)
        context['identity'] = self.request.session['identity']
        context['allow_cancel'] = self.request.session['ALLOW_CANCEL']
        return context


@login_required(login_url=reverse_lazy('index'))
def set_password(request):
    identity = request.session['identity']
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=identity['PSU_UUID'])

    if oam_status.set_password is True:
        form = ChangeOdinPasswordForm(user=request.user, data=request.POST or None)
    else:
        form = SetOdinPasswordForm(user=request.user, data=request.POST or None)

    if form.is_valid():

        if oam_status.set_password is False:
            oam_status.set_password = True
            oam_status.save(update_fields=['set_password'])

        # Updating the password logs out all other sessions for the user except the current one
        auth.update_session_auth_hash(request, request.user)

        logger.info("service=myinfo psu_uuid={0} password_set=true".format(
            identity['PSU_UUID']))
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    elif len(form.non_field_errors()) != 0:  # Valid data was posted, but API call was rejected
        logger.info("service=myinfo psu_uuid={0} password_set=false".format(
            identity['PSU_UUID']))

    # Consider rendering when the password expires. Eventually.
    return render(request, 'MyInfo/set_password.html', {
        'identity': identity,
        'form': form,
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

        logger.info("service=myinfo psu_uuid={0} directory_set=true".format(
            request.session['identity']['PSU_UUID']
        ))
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
        cell_phone = contact_info_form.cleaned_data['cell_phone']
        alternate_email = contact_info_form.cleaned_data['alternate_email']

        if cell_phone is None and alternate_email is None:  # pragma: no cover
            (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
            oam_status.set_contact_info = False
            oam_status.save()

        contact_info_form.save()

        logger.info("service=myinfo psu_uuid={0} contact_updated=true".format(
            request.session['identity']['PSU_UUID']
        ))
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
    logger.info("service=myinfo psu_uuid={0} welcomed=true".format(identity['PSU_UUID']))
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