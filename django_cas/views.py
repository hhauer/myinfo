"""CAS login/logout replacement views"""

from urllib.parse import urlencode
from urllib.parse import urljoin

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

__all__ = ['login', 'logout']

def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """

    _next = request.GET.get(REDIRECT_FIELD_NAME)
    if not _next:
        if settings.CAS_IGNORE_REFERER:
            _next = settings.CAS_REDIRECT_URL
        else:
            _next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        prefix = (('http://', 'https://')[request.is_secure()] +
                  request.get_host())
        if _next.startswith(prefix):
            _next = _next[len(prefix):]
    return _next


def _login_url(service):
    """Generates CAS login URL"""

    params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'url': protocol + host + next_page})
    return url


def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')
    service = _service_url(request, next_page)
    if ticket:
        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service, request=request)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(_login_url(service))
        else:
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    from django.contrib.auth import logout
    logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)
