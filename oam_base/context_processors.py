__author__ = 'justinm'


# Provide identity to templates.
# More secure than django.core.context_processors.request
# More efficient than manually passing request.session['identity'] to context in every view
def identity(request):
    if request.session is not None and 'identity' in request.session:
        return {'identity': request.session['identity']}
    return {}


# Tell template whether session can be canceled (logged out manually via logout link)
def cancel(request):
    if request.session is not None and 'ALLOW_CANCEL' in request.session:
        return {'allow_cancel': request.session['ALLOW_CANCEL']}
    return {}