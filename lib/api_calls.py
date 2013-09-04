'''
For managing API calls out to external resources such as sailpoint.
'''
import urllib
import urllib2
import json
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


# This function authenticates sailPoint and makes a call to the REST api pointed to by the link
# param. If there is postData, it is JSON encoded and posted to the link. This function returns
# a file-like object from which the response can be read.
def callSailpoint(link, data=None):
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, settings.SAILPOINT_SERVER_URL, settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD)
    auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth_handler)
    
    url = 'http://' + settings.SAILPOINT_SERVER_URL + '/identityiq/rest/custom/runRule/' + link
    if data:
        url += '?json=' + urllib.quote_plus(json.dumps(data))
    
    try:
        logger.debug("Making sailpoint call: {0}".format(url))
        response = opener.open(url)
        final_response = json.load(response)
        logger.debug("Sailpoint response: {0}".format(final_response))
    except urllib2.HTTPError as e:
        logger.critical("The following error occurred while attempting to contact sailpoint: {0} -- {1}".format(e.code, e.reason))
        return None
    except urllib2.URLError as e:
        logger.critical("The following error occurred while attempting to contact sailpoint: {0} -- {1}".format(e.code, e.reason))
        return None
    except ValueError:
        logger.critical("Sailpoint returned invalid JSON: {0}".format(response))
        return None

    return final_response or None

# This function turns a 9num into the user's identity information like name.
def identifyAccountPickup(spriden_id, birthdate, password): 
    # Stub for template work.
    if spriden_id == '123456789':
        return (True, {
            'PSU_UUID': '123456789',
            'DISPLAY_NAME': 'Stub User',
            'SPRIDEN_ID': '123456789'})
    
    # Build our packet to send to sailpoint.
    data = {
        "user_spriden_id" : spriden_id,
        "user_dob" : birthdate,
        "user_initpass" : password
    }
    
    result = callSailpoint('PSU_UI_ACCOUNT_CLAIM_AUTH', data)
    
    # If any of our tests fail, auth fails. 
    if result["DOB"] != "MATCH" or result["SPRIDEN_ID"] != "MATCH" or result["INITPASS"] != "MATCH":
        logger.info("Account pickup authentication failed with the following response: {0}".format(result))
        final_result = (False, None)
    elif "ERROR" in result:
        final_result = (False, None)
        # TODO: Should this be logged?
    else:
        final_result = (True, {
            "PSU_UUID": result["PSU_UUID"],
            "DISPLAY_NAME": result["IDENTITY_DISPLAY_NAME"],
            "SPRIDEN_ID": spriden_id
        })
    
    return final_result

# Identify a user with an expired password.
def identifyExpiredPassword(username, password):
    # TODO: Stubbed return (sailpoint rule context.authenticate)
    stub = {
        "PSU_UUID" : 'abc123',
        "DISPLAY_NAME" : "John Smith",
        "SPRIDEN_ID" : '123456789',
        "ODIN_NAME" : 'jsmith5',
        "EMAIL_ADDRESS" : "john.smith@pdx.edu",
    }
    return (True, stub)

# This function turns a UDC_ID into the user's identity information like name.
def identity_from_cas(udc_id):
    data = {'UDC_ID': udc_id}
    return callSailpoint('PSU_UI_IDENTIFY_UDC_ID', data)

# This function turns a PSU_UUID into the user's identity information like name.
def identity_from_psu_uuid(psu_uuid):
    data = {'PSU_UUID': psu_uuid}
    return callSailpoint('PSU_UI_IDENTIFY_UUID', data)
    
# This function returns the appropriate password constraints based on an identity.
def passwordConstraintsFromIdentity(identity):
    # TODO: Stubbed return
    return {
        'letter_count': 1,
        'number_count': 1,
        'special_count': 1,
        'minimum_count': 8,
        'maximum_count': 30,
    }
    return

# This function returns a list of potential odin names to choose from.
def truename_odin_names(identity):
    return callSailpoint('PSU_UI_TRUENAME_GEN_USERNAMES', identity)

# This function returns a list of potential email aliases to choose from.
def truename_email_aliases(identity):
    return callSailpoint('PSU_UI_TRUENAME_GEN_EMAILS', identity)
    
# This function calls out to sailpoint to begin a password update event.
def change_password(identity, new_password, old_password):
    data = {'PSU_UUID' : identity["PSU_UUID"],
            'password' : new_password,
            'old_password' : old_password,
    }
    
    status = callSailpoint('PSU_UI_UPDATE_PASSWORD', data)
    
    if "Success" in status:
        return (True, "")
    else:
        return (False, status["PasswordError"])
    return (True, "")

def launch_provisioning_workflow(identity, odin_name, email_alias):
    # TODO: Stubbed
    return

def password_reset(PSU_UUID, email, token, mode):
    data = {
        'PSU_UUID': PSU_UUID,
        'email': email,
        'token': token,
        'mode': mode,
    }
    
    callSailpoint('PSU_UI_PASSWORD_REMINDER', data)