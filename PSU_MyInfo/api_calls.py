'''
For managing API calls out to external resources such as sailpoint.
'''
import urllib2
import json
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


# This function authenticates sailPoint and makes a call to the REST api pointed to by the link
# param. If there is postData, it is JSON encoded and posted to the link. This function returns
# a file-like object from which the response can be read.
def callSailpoint(link, postData=None):
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, settings.SAILPOINT_SERVER_URL, settings.SAILPOINT_USER, settings.SAILPOINT_PASSWORD)
    auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth_handler)
    
    if postData:
        jsonData = json.dumps(postData)
        req = urllib2.Request('http://' + settings.SAILPOINT_SERVER_URL + '/iiq/rest/custom/' + link, jsonData, {'Content-Type': 'application/json'})
        return opener.open(req)
    
    return opener.open('http://' + settings.SAILPOINT_SERVER_URL + '/iiq/rest/custom/' + link)

# This function turns a 9num into the user's identity information like name.
def identifyAccountPickup(id_number, birthdate, password):
    
    # Stubbed return
    stub = {
        "PSU_UUID" : id_number,
        "DISPLAY_NAME" : "John Smith",
        "SPRIDEN_ID" : id_number,
    }
    return (True, stub)
    
    apiLink = 'getPSUPersonByKeyValue/psuid/' + id_number
    try:
        idData = json.load(callSailpoint(apiLink))
    except urllib2.HTTPError as e:
        logger.critical("An error {} occurred for user {}: {}".format(e.code, id_number, e.reason))
        return None
    except urllib2.URLError as e:
        logger.critical("There was an error contacting sailpoint for user {}: {}".format(id_number, e.reason))
        return None
    else:
        if 'Error' in idData:
            logger.critical("The following error was returned from sailpoint for 9num {} - {}".format(id_number, idData['Error']))
            return None
    
    return idData

# Identify a user with an expired password.
def identifyExpiredPassword(username, password):
    # TODO: Stubbed return
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
    # TODO: Stubbed return
    stub = {
        "PSU_UUID" : udc_id,
        "DISPLAY_NAME" : "John Smith",
        "SPRIDEN_ID" : '123456789',
        "ODIN_NAME" : 'jsmith5',
        "EMAIL_ADDRESS" : "john.smith@pdx.edu",
    }
    return stub

# This function turns a PSU_UUID into the user's identity information like name.
def identity_from_psu_uuid(psu_uuid):
    # TODO: Stubbed return
    stub = {
        "PSU_UUID" : psu_uuid,
        "DISPLAY_NAME" : "John Smith",
        "SPRIDEN_ID" : psu_uuid,
        "ODIN_NAME" : 'jsmith5',
        "EMAIL_ADDRESS" : "john.smith@pdx.edu",
    }
    return stub
    
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

# This function returns a list of potential odin names to choose from based on a 9-number.
def OdinNamesFromIdentity(identity):
    # TODO: Stubbed.
    return (('jsmith5', 'jsmith5'), ('j.smith', 'j.smith'), ('john.smith4', 'john.smith4'))

# This function returns a list of potential email aliases to choose from based on a 9-number.
def EmailAliasesFromIdentity(identity):
    # TODO: Stubbed
    return (('j.smith@pdx.edu', 'j.smith@pdx.edu'), 
            ('smith.j@pdx.edu', 'smith.j@pdx.edu'), 
            ('john.j.e.smith@pdx.edu', 'john.j.e.smith@pdx.edu'), 
            ('jsmith5@pdx.edu', 'jsmith5@pdx.edu'), 
            ('smitty@pdx.edu', 'smitty@pdx.edu'))

def launch_provisioning_workflow(identity, odin_name, email_aliases):
    # TODO: Stubbed
    return