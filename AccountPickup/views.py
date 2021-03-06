from datetime import date, timedelta

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.utils.decorators import method_decorator

from MyInfo.models import ContactInformation
from MyInfo.forms import ContactInformationForm

from AccountPickup.forms import AccountClaimLoginForm, AcceptAUPForm, OdinNameForm, EmailAliasForm
from AccountPickup.models import OAMStatusTracker

from lib.api_calls import truename_odin_names, truename_email_aliases, set_odin_username, set_email_alias, \
    get_provisioning_status, APIException

from brake.decorators import ratelimit

import logging

logger = logging.getLogger(__name__)


# The index of this module performs a non-CAS login to the AccountPickup system.
@ratelimit(method='POST', rate='30/m')
@ratelimit(method='POST', rate='250/h')
def index(request):
    limited = getattr(request, 'limited', False)
    if limited:
        return HttpResponseRedirect(reverse('rate_limited'))

    error_message = ""
    form = AccountClaimLoginForm(request.POST or None)

    if form.is_valid():
        # For some reason they already have a session. Let's get rid of it and start fresh.
        if request.session is not None:  # pragma: no cover
            request.session.flush()

        user = auth.authenticate(id_number=form.cleaned_data['id_number'],
                                 birth_date=form.cleaned_data['birth_date'],
                                 password=form.cleaned_data['auth_pass'],
                                 request=request)
        logger.debug("Account claim login attempt with ID: {0}".format(form.cleaned_data['id_number']))
        if user is not None:
            # Identity is valid.
            auth.login(request, user)
            logger.info(
                "service=myinfo page=accountclaim action=login status=success credential={0} psu_uuid={1}".format(
                    form.cleaned_data['id_number'], user.get_username()))

            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        # If identity is invalid, prompt re-entry.
        logger.info("service=myinfo page=accountclaim action=login status=error credential={0}".format(
                    form.cleaned_data['id_number']))
        error_message = ("This information was not recognized. "
                         "Ensure this information is correct and please try again. "
                         "If you continue to have difficulty, contact the Helpdesk (503-725-4357) for assistance.")

    return render(request, 'AccountPickup/index.html', {
        'form': form,
        'error': error_message,
    })


# Acceptable use policy.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def aup(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.agree_aup is not None and date.today() < oam_status.agree_aup + timedelta(weeks=26):
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    form = AcceptAUPForm(request.POST or None)

    if form.is_valid():
        oam_status.agree_aup = date.today()
        oam_status.save(update_fields=['agree_aup'])

        logger.info("service=myinfo page=accountclaim action=aup status=success psu_uuid={0}".format(
                    request.user.get_username()))
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    return render(request, 'AccountPickup/aup.html', {
        'form': form,
    })


# Password reset information.
# TODO: Refactor to merge with MyInfo.views.set_contact
# Probably best accomplished while reworking it for confirmation code feature
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
        oam_status.save(update_fields=['set_contact_info'])
        
        logger.info("service=myinfo page=accountclaim action=set_contact status=success psu_uuid={0}".format(
                    request.user.get_username()))
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))
    elif request.method == 'POST':
        logger.debug(_contact_info)
        logger.debug(request.POST)

    return render(request, 'AccountPickup/contact_info.html', {
        'form': contact_form,
    })


class SelectOdinNameView(FormView):
    template_name = 'AccountPickup/odin_name.html'
    form_class = OdinNameForm
    success_url = reverse_lazy('AccountPickup:next_step')

    @method_decorator(login_required(login_url=reverse_lazy('AccountPickup:index')))
    def dispatch(self, request, *args, **kwargs):
        # If someone has already completed this step, move them along:
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.user.get_username())
        if oam_status.select_odin_username is True:
            return HttpResponseRedirect(self.success_url)

        self._get_odin_names(request)

        return super(SelectOdinNameView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def _get_odin_names(request):
        # Get possible odin names
        if 'TRUENAME_USERNAMES' not in request.session:
            request.session['TRUENAME_USERNAMES'] = truename_odin_names(request.session['identity'])
            # If truename server is not responding, don't give user empty list
            if len(request.session['TRUENAME_USERNAMES']) == 0:
                raise APIException(
                    "Truename API call failed: No names found. psu_uuid={0}".format(request.user.get_username()))

    def get_form_kwargs(self):
        kwargs = super(SelectOdinNameView, self).get_form_kwargs()
        kwargs.update({'session': self.request.session})
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(SelectOdinNameView, self).form_valid(form)


class SelectAliasView(FormView):
    template_name = 'AccountPickup/email_alias.html'
    form_class = EmailAliasForm
    success_url = reverse_lazy('AccountPickup:next_step')

    @method_decorator(login_required(login_url=reverse_lazy('AccountPickup:index')))
    def dispatch(self, request, *args, **kwargs):
        # If someone has already completed this step, move them along:
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
        if oam_status.select_email_alias is True:
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        self._get_aliases(request)
        return super(SelectAliasView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def _get_aliases(request):
        # Get possible email aliases
        if 'TRUENAME_EMAILS' not in request.session:
            request.session['TRUENAME_EMAILS'] = truename_email_aliases(request.session['identity'])

            if len(request.session['TRUENAME_EMAILS']) == 0:
                # Truename down, don't offer empty list
                raise APIException(
                    "Truename API call failed: No aliases found. psu_uuid={0}".format(request.user.get_username()))

            # Prepend a "None" option at the start of the emails.
            request.session['TRUENAME_EMAILS'].insert(0, 'None')

    def get_form_kwargs(self):
        kwargs = super(SelectAliasView, self).get_form_kwargs()
        kwargs.update({'session': self.request.session})
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(SelectAliasView, self).form_valid(form)


# Pause and wait for provisioning to finish if necessary. This page uses AJAX calls to determine
# when it's safe to move on to setting a password.
@login_required(login_url=reverse_lazy('AccountPickup:index'))
def wait_for_provisioning(request):
    # If someone has already completed this step, move them along:
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    if oam_status.provisioned is True:
        return HttpResponseRedirect(reverse('AccountPickup:next_step'))

    return render(request, 'AccountPickup/wait_for_provisioning.html', {
    })


@login_required(login_url=reverse_lazy('AccountPickup:index'))
def oam_status_router(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=request.session['identity']['PSU_UUID'])
    request.session['ALLOW_CANCEL'] = False

    if 'CHECKED_IIQ' not in request.session:
        provision_status = get_provisioning_status(request.session['identity']['PSU_UUID'])

        if len(provision_status) == 0:
            raise APIException("IIQ API call failed: no status. psu_uuid={0}".format(request.user.get_username()))

        # If they've already been through MyInfo, provisioned will be true and we don't want to pester them
        # a second time to pick an alias if previously they selected "none."
        if oam_status.select_email_alias is False:
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
        request.session['ALLOW_CANCEL'] = True
        # OAM has been completed. Dump them to MyInfo main page.
        return HttpResponseRedirect(reverse('MyInfo:pick_action'))
