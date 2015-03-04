"""
Created on Mar 25, 2013

@author: hhauer
"""
from django.contrib.auth import get_user_model
from lib.api_calls import identify_oam_login, identity_from_psu_uuid

import logging
logger = logging.getLogger(__name__)


# This class defines an authentication backend for bypassing CAS, used to auth during
# account claim.
class AccountPickupBackend(object):
    @staticmethod
    def authenticate(request, id_number=None, birth_date=None, password=None):
        _user = get_user_model()

        if not id_number or not birth_date or not password:
            return None

        # Try activation code login
        auth_pass = "{:%m%d%y}{}".format(birth_date, password)
        identity = identify_oam_login(id_number, auth_pass)

        # If user lost original activation code, try with code as standard password
        if identity is None:
            identity = identify_oam_login(id_number, password)

        if identity is not None:
            request.session['identity'] = identity
        else:
            return None
        
        try:
            user = _user.objects.get(username=identity['PSU_UUID'])
        except _user.DoesNotExist:
            # user will have an "unusable" password
            user = _user.objects.create_user(identity['PSU_UUID'], password=None)
        return user

    @staticmethod
    def get_user(user_id):
        _user = get_user_model()

        try:
            return _user.objects.get(pk=user_id)
        except _user.DoesNotExist:
            return None


# Generic front-page login handler for OAM. Passes the buck to Sailpoint.
class OAMLoginBackend(object):
    @staticmethod
    def authenticate(request, username=None, password=None):
        _user = get_user_model()

        if not username or not password:
            return None
        
        identity = identify_oam_login(username, password)
        if identity is not None:
            request.session['identity'] = identity
        else:
            return None

        try:
            user = _user.objects.get(username=identity['PSU_UUID'])
        except _user.DoesNotExist:
            # user will have an "unusable" password
            user = _user.objects.create_user(identity['PSU_UUID'], password=None)
        return user

    @staticmethod
    def get_user(user_id):
        _user = get_user_model()

        try:
            return _user.objects.get(pk=user_id)
        except _user.DoesNotExist:
            return None


# This class manages the login if the user forgot their password.
class ForgotPasswordBackend(object):
    @staticmethod
    def authenticate(request, psu_uuid=None):
        _user = get_user_model()

        if not psu_uuid:
            return None
        
        # We got here by decrypting a cryptographically-signed token. We assume the psu_uuid is valid.
        # TODO: Might want to check it just to be sure, but low-priority.
        
        request.session['identity'] = identity_from_psu_uuid(psu_uuid)
        logger.debug("service=myinfo psu_uuid=" + psu_uuid + " authenticate=password_reset")

        try:
            user = _user.objects.get(username=psu_uuid)
        except _user.DoesNotExist:
            # user will have an "unusable" password
            user = _user.objects.create_user(psu_uuid, password=None)
        return user
    
    @staticmethod
    def get_user(user_id):
        _user = get_user_model()

        try:
            return _user.objects.get(pk=user_id)
        except _user.DoesNotExist:
            return None