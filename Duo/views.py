import logging
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from Duo import duo_web
from lib.api_calls import APIException

logger = logging.getLogger(__name__)


# Duo Login
@login_required(login_url=reverse_lazy('duoLogin'))
def login(request):
    if 'identity' not in request.session or 'ODIN_NAME' not in request.session['identity']:
        # Error state
        raise APIException("Attempted to go to Duo Login without a valid identity dictionary of ODIN_NAME dictionary value")

    # TODO: In production username will be PSU_UUID, so we need to do some work to get the odin username
    if request.method == 'GET':
        sig_request = duo_web.sign_request(settings.DUO_IKEY, settings.DUO_SKEY, settings.DUO_AKEY, request.session['identity']['ODIN_NAME'])
        return render(request, 'login.html', {
            'sig_request': sig_request,
            'host': settings.DUO_HOST
        }
                      )
    elif request.method == 'POST':
        sig_response = request.POST.get('sig_response', '')
        duo_web.verify_response(settings.DUO_IKEY, settings.DUO_SKEY, settings.DUO_AKEY, sig_response)
        return HttpResponseRedirect(request.path)