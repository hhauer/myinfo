import logging
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from Duo import duo_web
from lib.api_calls import provision_duo

logger = logging.getLogger(__name__)


# Duo Login
@login_required(login_url=reverse_lazy('duoLogin'))
def login(request):
    # Interaction with Duo occurs entirely over JavaScript, but leverages a widget designed for login.
    # If the user selects "login" they will post back to this page, but we don't actually want to do anything but
    # re-draw the widget.

    # Duo API returns a dict.
    duo = provision_duo(request.user.username)

    if duo['status'] == 'error':
        if duo['reason'] == 'noidentity':
            raise NoIdentityException("No matching identity found for user currently logged into MyInfo.")
        elif duo['reason'] == 'notemployee':
            logger.error("Non-employee user attempting to access Duo self-registration. " + request.user.username)
            return HttpResponseRedirect(reverse('AccountPickup:next_step'))
        else:
            raise DuoSecurityException("Duo returned an exception: " + duo['message'])

    if 'identity' not in request.session:
        raise NoIdentityException("No identity information in the session.")

    if 'ODIN_NAME' not in request.session['identity']:
        raise NoIdentityException("Identity in session, but no ODIN_NAME attribute.")

    odin_username = request.session['identity']['ODIN_NAME']

    sig_request = duo_web.sign_request(settings.DUO_IKEY, settings.DUO_SKEY, settings.DUO_AKEY, odin_username)
    return render(request, 'login.html', {
        'sig_request': sig_request,
        'host': settings.DUO_HOST
    })


class NoIdentityException(Exception):
    pass


class DuoSecurityException(Exception):
    pass