
from django.views.defaults import server_error


def custom_error(request):
    # Kill the session for data security at kiosks
    if request.session is not None:
        request.session.flush()
    # Call out to built-in 500 view
    return server_error(request)