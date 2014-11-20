'''
For managing API calls out to external resources such as sailpoint.
'''
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


# This function authenticates sailPoint and makes a call to the REST api pointed to by the link
# param. If there is postData, it is JSON encoded and posted to the link. This function returns
# a file-like object from which the response can be read.
def call_iiq(link, data=None):
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, settings.SAILPOINT_SERVER_URL, settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_handler)
    
    url = 'https://' + settings.SAILPOINT_SERVER_URL + '/identityiq/rest/custom/runRule/' + link
    if data:
        url += '?json=' + urllib.parse.quote_plus(json.dumps(data))
    
    try:
        logger.debug("Making sailpoint call: {0}".format(url))
        response = opener.open(url)
        response_body = response.read()
        final_response = json.loads(response_body.decode('UTF-8'))
        logger.debug("Sailpoint response: {0}".format(final_response))
    except urllib.error.HTTPError as e:
        if hasattr(e, 'reason'):
            logger.critical("An HTTPError occurred attempting to reach sailpoint with the following reason: {0}".format(e.reason))
        if hasattr(e, 'code'):
            logger.critical("An HTTPError occurred attempting to reach sailpoint with the following code: {0}".format(e.code))
        return None
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            logger.critical("An URLError occurred attempting to reach sailpoint with the following reason: {0}".format(e.reason))
        if hasattr(e, 'code'):
            logger.critical("An URLError occurred attempting to reach sailpoint with the following code: {0}".format(e.code))
        return None
    except ValueError:
        logger.critical("Sailpoint returned invalid JSON: {0}".format(response))
        return None

    return final_response or None

# Identify a user with an expired password.
def identify_oam_login(username, password):
    if settings.DEVELOPMENT == True:
        stub = {
            "PSU_UUID" : username,
            "DISPLAY_NAME" : "Development User",
            "SPRIDEN_ID" : '123456789',
            "ODIN_NAME" : 'jsmith5',
            "EMAIL_ADDRESS" : "john.smith@pdx.edu",
            "PSU_PUBLISH" : True,
        }
        
        return stub
    
    data = {
        'username': username,
        'password': password,
    }
    res = call_iiq('PSU_UI_MYINFO_LOGIN_PASSWORD', data)

    # Massage PSU_PUBLISH:
    if "PSU_PUBLISH" in res:
        if res["PSU_PUBLISH"] is not None and res["PSU_PUBLISH"].lower() == "yes":
            res["PSU_PUBLISH"] = True
        else:
            res["PSU_PUBLISH"] = False
    
    if "ERROR" in res:
        return None
    else:
        return res

# This function turns a PSU_UUID into the user's identity information like name.
def identity_from_psu_uuid(psu_uuid):
    if settings.DEVELOPMENT == True:
        return {
            "PSU_UUID" : psu_uuid,
            "DISPLAY_NAME" : "Development User - UUID",
            "SPRIDEN_ID" : '123456789',
            "ODIN_NAME" : 'jsmith5',
            "EMAIL_ADDRESS" : "john.smith@pdx.edu",
            "PSU_PUBLISH" : True,
        }
        
    data = {'PSU_UUID': psu_uuid}
    results = call_iiq('PSU_UI_MYINFO_LOGIN_UUID', data)

    # Massage PSU_PUBLISH:
    if "PSU_PUBLISH" in results:
        if results["PSU_PUBLISH"] is not None and results["PSU_PUBLISH"].lower() == "yes":
            results["PSU_PUBLISH"] = True
        else:
            results["PSU_PUBLISH"] = False

    return results
    
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

    usernames = call_iiq('PSU_UI_TRUENAME_GEN_USERNAMES', identity)
    return usernames["GENERATED_USERNAMES"]

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

    emails = call_iiq('PSU_UI_TRUENAME_GEN_EMAILS', identity)
    return emails["GENERATED_EMAILS"]
    
# This function calls out to sailpoint to begin a password update event.
def change_password(identity, new_password, old_password):
    if settings.DEVELOPMENT == True:
        return (True, "Development password change.")

    data = {'PSU_UUID' : identity["PSU_UUID"],
            'password' : new_password,
            'old_password' : old_password,
    }
    
    status = call_iiq('PSU_UI_UPDATE_PASSWORD', data)
    
    if "Success" in status:
        return (True, "Password changed succesfully.")
    elif "Error" in status:
        return (False, status["Error"])
    else:
        return (False, status["PasswordError"])

def set_odin_username(identity, odin_name):
    data = {
        'psu_uuid': identity["PSU_UUID"],
        'name': odin_name,
    }

    res = call_iiq('PSU_UI_SET_ODIN_USERNAME', data)
    return res

def set_email_alias(identity, email_alias):
    data = {
        'psu_uuid': identity["PSU_UUID"],
        'alias': email_alias,
    }

    res = call_iiq('PSU_UI_SET_EMAIL_ALIAS', data)
    return res

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
    call_iiq('PSU_UI_RESET_EMAIL', data)

def password_reset_sms(number, token):
    if settings.DEVELOPMENT == True:
        logger.debug("password_reset_sms called with the following number: {0} and token: {1}".format(number, token))
        return # In development short-circuit the send call.
    
    data = {
    'sms_number': number,
    'sms_reset_code': token,
    }
    call_iiq('PSU_UI_RESET_SMS', data)

# Query IIQ for OamStatus information.
def get_provisioning_status(psu_uuid):
    data = {
        'psu_uuid': psu_uuid,
    }

    return call_iiq('PSU_UI_GET_PROVISIONING_STATUS', data)