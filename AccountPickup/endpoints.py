'''
AJAX Endpoints
'''

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from AccountPickup.models import OAMStatusTracker

# Sleep used for development to add a delay to the wait for provisioning page.
from time import sleep

import logging
logger = logging.getLogger(__name__)


@login_required(login_url=reverse_lazy('AccountPickup:index'))
def check_provisioning(request):
    (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid = request.session['identity']['PSU_UUID'])
    
    if settings.DEVELOPMENT == True:
        sleep(10) # Force a brief pause so the "wait for provisioning" page is visible.
        oam_status.provisioned = True
        oam_status.save()
            
    
    return {'complete': oam_status.provisioned}