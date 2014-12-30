"""
For managing API calls out to external resources such as sailpoint.
"""
# import urllib.request, urllib.parse, urllib.error
# import urllib.request, urllib.error, urllib.parse
# import json
from django.conf import settings
from AccountPickup.models import OAMStatusTracker
import logging
import requests

logger = logging.getLogger(__name__)


def iiq_auth():
    return settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD


# Identify a user with an expired password.
def identify_oam_login(username, password):
    if settings.DEVELOPMENT is True:
        if username == "000000000":
            return None  # Provide 'known bad' stub for testing
        stub = {
            "PSU_UUID": username,
            "DISPLAY_NAME": "Development User",
            "SPRIDEN_ID": '123456789',
            "ODIN_NAME": 'jsmith5',
            "EMAIL_ADDRESS": "john.smith@pdx.edu",
            "PSU_PUBLISH": True,
        }

        return stub

    data = {
        'username': username,
        'password': password,
    }

    url = "https://{}/identityiq/rest/custom/login/password".format(
        settings.SAILPOINT_SERVER_URL,
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False, data=data)

    res = r.json()

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
    if settings.DEVELOPMENT is True:
        return {
            "PSU_UUID": psu_uuid,
            "DISPLAY_NAME": "Development User - UUID",
            "SPRIDEN_ID": '123456789',
            "ODIN_NAME": 'jsmith5',
            "EMAIL_ADDRESS": "john.smith@pdx.edu",
            "PSU_PUBLISH": True,
        }

    data = {'PSU_UUID': psu_uuid}

    url = "https://{}/identityiq/rest/custom/login/uuid".format(
        settings.SAILPOINT_SERVER_URL,
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False, data=data)

    results = r.json()

    # Massage PSU_PUBLISH:
    if "PSU_PUBLISH" in results:
        if results["PSU_PUBLISH"] is not None and results["PSU_PUBLISH"].lower() == "yes":
            results["PSU_PUBLISH"] = True
        else:
            results["PSU_PUBLISH"] = False

    return results


# This function returns the appropriate password constraints based on an identity.
def passwordConstraintsFromIdentity(identity):  # is this function used? PEP8 says rename to lower_case
    # TODO: Stubbed return
    return {
        'letter_count': 1,
        'number_count': 1,
        'special_count': 1,
        'minimum_count': 8,
        'maximum_count': 30,
    }


# This function returns a list of potential odin names to choose from.
def truename_odin_names(identity):
    if settings.DEVELOPMENT is True:
        stub = [
            'Odin Name 1 - DEV',
            'Odin Name 2 - DEV',
            'Odin Name 3 - DEV',
            'Odin Name 4 - DEV',
        ]
        return stub

    url = "https://{}/identityiq/rest/custom/odinNames/{}".format(
        settings.SAILPOINT_SERVER_URL,
        identity['PSU_UUID'],
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False)
    return r.json()


# This function returns a list of potential email aliases to choose from.
def truename_email_aliases(identity):
    if settings.DEVELOPMENT is True:
        stub = [
            'Email Alias 1 - DEV',
            'Email Alias 2 - DEV',
            'Email Alias 3 - DEV',
            'Email Alias 4 - DEV',
        ]
        return stub

    url = "https://{}/identityiq/rest/custom/emailAliases/{}".format(
        settings.SAILPOINT_SERVER_URL,
        identity['PSU_UUID'],
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False)
    return r.json()


# This function calls out to sailpoint to begin a password update event.
def change_password(identity, new_password, old_password):
    if settings.DEVELOPMENT is True:
        return True, "Development password change."

    data = {'PSU_UUID': identity["PSU_UUID"],
            'password': new_password,
            'old_password': old_password,
            }

    url = "https://{}/identityiq/rest/custom/changePassword".format(
        settings.SAILPOINT_SERVER_URL,
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), data=data, verify=False)
    result = r.json()

    status = result["Status"]

    if status == "Success":
        return True, "Password changed successfully."
    elif "PasswordErrors" in result:
        return False, result["PasswordErrors"]
    else:
        return False, [result["Error"]]  # Make it a list of one item, for the display logic.


def set_odin_username(identity, odin_name):
    if settings.DEVELOPMENT is True:
        return "SUCCESS"

    url = "https://{}/identityiq/rest/custom/setOdin/{}".format(
        settings.SAILPOINT_SERVER_URL,
        identity['PSU_UUID'],
    )

    payload = {
        'odin_name': odin_name,
    }

    r = requests.post(url,
                      data=payload,
                      auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD),
                      verify=False)
    return r.json()


def set_email_alias(identity, email_alias):
    if settings.DEVELOPMENT is True:
        return "SUCCESS"

    data = {
        'psu_uuid': identity["PSU_UUID"],
        'email': email_alias,
    }

    url = "https://{}/identityiq/rest/custom/setPreferredEmail/{}".format(
        settings.SAILPOINT_SERVER_URL,
        identity["PSU_UUID"],
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False,
                      data=data)

    res = r.json()
    return res


# Send a password reset email.
def password_reset_email(psu_uuid, email, token):
    if settings.DEVELOPMENT is True:
        logger.debug("password_reset_email called with the following email: {0} and token: {1}".format(email, token))
        return  # In development short-circuit the send call.

    data = {
        'PSU_UUID': psu_uuid,
        'email': email,
        'reset_code': token,
    }

    url = "https://{}/identityiq/rest/custom/passwordReset/email".format(
        settings.SAILPOINT_SERVER_URL,
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False,
                      data=data)

    return r.json()


def password_reset_sms(number, token):
    if settings.DEVELOPMENT is True:
        logger.debug("password_reset_sms called with the following number: {0} and token: {1}".format(number, token))
        return  # In development short-circuit the send call.

    data = {
        'sms_number': number,
        'reset_code': token,
    }

    url = "https://{}/identityiq/rest/custom/passwordReset/sms".format(
        settings.SAILPOINT_SERVER_URL,
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False,
                      data=data)

    return r.json()


# Query IIQ for OamStatus information.
def get_provisioning_status(psu_uuid):
    if settings.DEVELOPMENT is True:
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=psu_uuid)
        return {
            "ODIN_SELECTED": oam_status.select_odin_username,
            "ALIAS_SELECTED": oam_status.select_email_alias,
            "PROVISIONED": oam_status.provisioned,
            "WELCOMED": oam_status.welcome_displayed,
            "PASSWORD_SET": oam_status.set_password,
        }

    url = "https://{}/identityiq/rest/custom/provisioningStatus/{}".format(
        settings.SAILPOINT_SERVER_URL,
        psu_uuid,
    )

    r = requests.post(url, auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD), verify=False)

    return r.json()
