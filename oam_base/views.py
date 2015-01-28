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
    remote_addr = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    logger.info("service=myinfo remote_addr=" + remote_addr + " rate_limited=true")
    return render(request, 'rate_limited.html')