from django.shortcuts import render
from django.views.defaults import server_error

import logging
logger = logging.getLogger(__name__)


def custom_error(request):
    # Kill the session for data security at kiosks
    if request.session is not None:
        request.session.flush()
    # Call out to built-in 500 view
    return server_error(request)


# Render an error page that the user has been subjected to rate limiting.
def rate_limited(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', "not provided")
    remote_addr = request.META.get('REMOTE_ADDR', "not provided")

    logger.info("Ratelimit view reached. X-FORWARDED-FOR: " + x_forwarded_for + " REMOTE_ADDR: " + remote_addr)

    return render(request, 'rate_limited.html')