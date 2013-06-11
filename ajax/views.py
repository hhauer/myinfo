from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from django.utils.importlib import import_module
from django.utils.log import getLogger
from django.core.serializers.json import DjangoJSONEncoder
from ajax.exceptions import AJAXError, NotRegistered
from ajax.decorators import json_response
import ajax


logger = getLogger('django.request')


@json_response
def endpoint_loader(request, application, model, **kwargs):
    """Load an AJAX endpoint.

    This will load either an ad-hoc endpoint or it will load up a model
    endpoint depending on what it finds. It first attempts to load ``model``
    as if it were an ad-hoc endpoint. Alternatively, it will attempt to see if
    there is a ``ModelEndpoint`` for the given ``model``.
    """
    if request.method != "POST":
        raise AJAXError(400, _('Invalid HTTP method used.'))

    try:
        module = import_module('%s.endpoints' % application)
    except ImportError, e:
        if settings.DEBUG:
            raise e
        else:
            raise AJAXError(404, _('AJAX endpoint does not exist.'))

    if hasattr(module, model):
        # This is an ad-hoc endpoint
        endpoint = getattr(module, model)
    else:
        # This is a model endpoint
        method = kwargs.get('method', 'create').lower()
        try:
            del kwargs['method']
        except:
            pass

        try:
            model_endpoint = ajax.endpoint.load(model, application, method,
                **kwargs)
            if not model_endpoint.authenticate(request, application, method):
                raise AJAXError(403, _('User is not authorized.'))

            endpoint = getattr(model_endpoint, method, False)

            if not endpoint:
                raise AJAXError(404, _('Invalid method.'))
        except NotRegistered:
            raise AJAXError(500, _('Invalid model.'))

    data = endpoint(request)
    if isinstance(data, HttpResponse):
        return data
    else:
        payload = {
            'success': True,
            'data': data,
        }
        return HttpResponse(json.dumps(payload, cls=DjangoJSONEncoder,
            separators=(',', ':')))
