'''
AJAX Endpoints
'''

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from AccountPickup.forms import pickOdinName, EmailAliasForm
from lib.api_calls import launch_provisioning_workflow

from MyInfo.models import UserDataItem

import logging
logger = logging.getLogger(__name__)


@login_required(login_url='/AccountClaim/')
def provision_new_user(request):
    logger.debug("Provision new user launched with the following data: {0}".format(request.POST))
    
    # Pass in the session to the odinForm so that it can get appropriate name options.
    odinForm = pickOdinName(request.session, request.POST or None)
    mailForm = EmailAliasForm(request.session, request.POST or None)
    
    # Run both validations before the test so that short-circuiting does not bypass a validation.
    odin_valid = odinForm.is_valid()
    mail_valid = mailForm.is_valid()
        
    if odin_valid and mail_valid:
        logger.debug("Odin name selected: {0}".format(odinForm.cleaned_data['name']))
        logger.debug("Email Aliases: {0}".format(mailForm.cleaned_data))
        
        # After this point, the provisioning will have started so if the user re-logs after this
        # they will need to be at the MyInfo:index step.
        request.session['NEXT'] = 'MyInfo:index'
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID'], 
                                    key_name ='MYINFO_PICKUP_STATE').update(key_valu = 'MyInfo:index')
        
        # Send the information to sailpoint to begin provisioning.
        odin_name = request.session['TRUENAME_USERNAMES'][odinForm.cleaned_data['name']]
        email_alias = request.session['TRUENAME_EMAILS'][mailForm.cleaned_data['aliases']]
        launch_provisioning_workflow(request.session['identity'], odin_name, email_alias)
    
    return {'status' : 'Forward', 'URL' : reverse('MyInfo:update')}