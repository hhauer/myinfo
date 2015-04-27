import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import Error
from django.utils.decorators import method_decorator
from django.views.generic import FormView, UpdateView

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
            logger.info("service=myinfo page=myinfo action=login status=success credential={0} psu_uuid={1}".format(
                        login_form.cleaned_data['username'], user.get_username()))

            # Head to the oam status router in case they have any unmet oam tasks.
            return HttpResponseRedirect(reverse("AccountPickup:next_step"))

        # If identity is invalid, log and prompt re-entry.
        logger.info("service=myinfo page=myinfo action=login status=failed credential={0}".format(
                    login_form.cleaned_data['username']))
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


@login_required(login_url=reverse_lazy('index'))
def set_password(request):

    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.user.get_username())
    if oam_status.set_password is True:
        form = ChangeOdinPasswordForm
    else:
        form = SetOdinPasswordForm

    return password_change(request=request, template_name='MyInfo/set_password.html',
                           post_change_redirect=reverse('AccountPickup:next_step'), password_change_form=form)


class DirectoryView(UpdateView):

    template_name = 'MyInfo/set_directory.html'
    model = DirectoryInformation
    fields = '__all__'
    success_url = reverse_lazy('AccountPickup:next_step')

    @method_decorator(login_required(login_url=reverse_lazy('index')))
    def dispatch(self, request, *args, **kwargs):
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.user.get_username())

        # Are they an employee with information to update?
        if request.session['identity']['PSU_PUBLISH'] is False:
            oam_status.set_directory = True
            oam_status.save(update_fields=['set_directory'])
            return HttpResponseRedirect(self.success_url)  # If not, they shouldn't be here

        return super(DirectoryView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):

        (directory_info, _) = DirectoryInformation.objects.get_or_create(psu_uuid=self.request.user.get_username())
        return directory_info

    def form_valid(self, form):
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.request.user.get_username())
        if oam_status.set_directory is False:
            oam_status.set_directory = True
            oam_status.save(update_fields=['set_directory'])

        logger.info("service=myinfo psu_uuid={0} directory_set=true".format(self.request.user.get_username()))
        # Parent class saves form/object
        return super(DirectoryView, self).form_valid(form)


# TODO: refactor to merge with AccountPickup contact info view
# Probably best done when confirmation/notification functionality is added
@login_required(login_url=reverse_lazy('index'))
def set_contact(request):
    # We don't check OAMStatusTracker because if they don't have contact info set they will be sent to the
    # AccountPickup version of this page. This is just for changing existing contact info.

    # Build our password reset information form.
    (contact_info, _) = ContactInformation.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    contact_info_form = ContactInformationForm(request.POST or None, instance=contact_info)

    if contact_info_form.is_valid():

        contact_info_form.save()
        logger.info("service=myinfo page=myinfo action=update_contact status=success psu_uuid={0}".format(
                    request.user.get_username()))
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    return render(request, 'MyInfo/set_contact.html', {
        'form': contact_info_form,
    })


@login_required(login_url=reverse_lazy('index'))
def welcome_landing(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    oam_status.welcome_displayed = True
    oam_status.save(update_fields=['welcome_displayed'])

    identity = request.session['identity']
    # Kill the session. They are now done.
    request.session.flush()

    logger.info("service=myinfo page=myinfo action=welcome status=success psu_uuid={0}".format(identity['PSU_UUID']))
    return render(request, 'MyInfo/welcome_landing.html', {'identity': identity, })


# Handle an F5 ping.
def ping(request):
    # Can we get something from the database?
    try:
        _ = Department.objects.all()[0]
        return HttpResponse("Success")
    except (Error, IndexError):
        return HttpResponse("Database not available!")
