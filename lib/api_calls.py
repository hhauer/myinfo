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
        if hasattr(e, 'reason'):
            logger.critical("An HTTPError occurred attempting to reach sailpoint with the following reason: {0}".format(e.reason))
        if hasattr(e, 'code'):
            logger.critical("An HTTPError occurred attempting to reach sailpoint with the following code: {0}".format(e.code))
        return None
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            logger.critical("An URLError occurred attempting to reach sailpoint with the following reason: {0}".format(e.reason))
        if hasattr(e, 'code'):
            logger.critical("An URLError occurred attempting to reach sailpoint with the following code: {0}".format(e.code))
        return None
    except ValueError:
        logger.critical("Sailpoint returned invalid JSON: {0}".format(response))
        return None

    return final_response or None

# This function turns a 9num into the user's identity information like name.
def identifyAccountPickup(spriden_id, birthdate, password):
    if settings.DEVELOPMENT == True:
        return (True, {
            'PSU_UUID': spriden_id,
            'DISPLAY_NAME': 'Development User',
            'SPRIDEN_ID': spriden_id})

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

# Identify a user with an expired password. TODO: GENERIC OAM LOGIN
def identify_oam_login(username, password):
    if settings.DEVELOPMENT == True:
        stub = {
            "PSU_UUID" : username,
            "DISPLAY_NAME" : "Development User",
            "SPRIDEN_ID" : '123456789',
            "ODIN_NAME" : 'jsmith5',
            "EMAIL_ADDRESS" : "john.smith@pdx.edu",
            "PSU_PUBLISH" : True
        }
        
        return stub
    
    data = {
        'username': username,
        'password': password,
    }
    res = callSailpoint('PSU_UI_IDENTIFY_EXPIRED_PASS', data)
    
    if "ERROR" in res:
        return None
    else:
        return res

# This function turns a UDC_ID into the user's identity information like name.
def identity_from_cas(udc_id):
    if settings.DEVELOPMENT == True:
        return {
            "PSU_UUID" : udc_id,
            "DISPLAY_NAME" : "Development User - CAS",
            "SPRIDEN_ID" : '123456789',
            "ODIN_NAME" : 'jsmith5',
            "EMAIL_ADDRESS" : "john.smith@pdx.edu",
        }
        
    data = {'UDC_ID': udc_id}
    return callSailpoint('PSU_UI_IDENTIFY_UDC_ID', data)

# This function turns a PSU_UUID into the user's identity information like name.
def identity_from_psu_uuid(psu_uuid):
    if settings.DEVELOPMENT == True:
        return {
            "PSU_UUID" : psu_uuid,
            "DISPLAY_NAME" : "Development User - UUID",
            "SPRIDEN_ID" : '123456789',
            "ODIN_NAME" : 'jsmith5',
            "EMAIL_ADDRESS" : "john.smith@pdx.edu",
        }
        
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
    if settings.DEVELOPMENT == True:
        stub = [
            'Odin Name 1 - DEV',
            'Odin Name 2 - DEV',
            'Odin Name 3 - DEV',
            'Odin Name 4 - DEV',
        ]
        return stub
        
    return callSailpoint('PSU_UI_TRUENAME_GEN_USERNAMES', identity)

# This function returns a list of potential email aliases to choose from.
def truename_email_aliases(identity):
    if settings.DEVELOPMENT == True:
        stub = [
            'Email Alias 1 - DEV',
            'Email Alias 2 - DEV',
            'Email Alias 3 - DEV',
            'Email Alias 4 - DEV',
        ]
        return stub
        
    return callSailpoint('PSU_UI_TRUENAME_GEN_EMAILS', identity)
    
# This function calls out to sailpoint to begin a password update event.
def change_password(identity, new_password, old_password):
    if settings.DEVELOPMENT == True:
        return (False, "Password change always fails in development.")

    data = {'PSU_UUID' : identity["PSU_UUID"],
            'password' : new_password,
            'old_password' : old_password,
    }
    
    status = callSailpoint('PSU_UI_UPDATE_PASSWORD', data)
    
    if "Success" in status:
        return (True, "")
    elif "Error" in status:
        return (False, status["Error"])
    else:
        return (False, status["PasswordError"])

def launch_provisioning_workflow(identity, odin_name, email_alias):
    # TODO: Stubbed
    return

# Send a password reset email.
def password_reset_email(PSU_UUID, email, token):
    if settings.DEVELOPMENT == True:
        logger.debug("password_reset_email called with the following email: {0} and token: {1}".format(email, token))
        return # In development short-circuit the send call.
    
    data = {
        'PSU_UUID': PSU_UUID,
        'email': email,
        'token': token,
    }
    callSailpoint('PSU_UI_RESET_EMAIL', data)

def password_reset_sms(number, token):
    if settings.DEVELOPMENT == True:
        logger.debug("password_reset_sms called with the following number: {0} and token: {1}".format(number, token))
        return # In development short-circuit the send call.
    
    data = {
    'sms_number': number,
    'sms_reset_code': token,
    }
    callSailpoint('PSU_UI_RESET_SMS', data)