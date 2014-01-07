'''
Created on Mar 25, 2013

@author: hhauer
'''
from django.contrib.auth.models import User
from lib.api_calls import identifyAccountPickup, identify_oam_login, identity_from_psu_uuid

import logging
logger = logging.getLogger(__name__)

# This class defines an authentication backend for bypassing CAS, used to auth during
# account claim.
class AccountPickupBackend(object):
    def authenticate(self, request, id_number=None, birth_date=None, password=None):
        if not id_number or not birth_date or not password:
            return None
        
        success, identity = identifyAccountPickup(id_number, birth_date, password)
        if success:
            request.session['identity'] = identity
        else:
            return None
        
        try:
            user = User.objects.get(username=identity['PSU_UUID'])
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(identity['PSU_UUID'], password=None)
        return user


    def get_user(self, userId):
        try:
            return User.objects.get(pk=userId)
        except User.DoesNotExist:
            return None

# Generic front-page login handler for OAM. Passes the buck to Sailpoint.
class OAMLoginBackend(object):
    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            return None
        
        identity = identify_oam_login(username, password)
        if identity is not None:
            request.session['identity'] = identity
        else:
            return None

        try:
            user = User.objects.get(username=identity['PSU_UUID'])
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(identity['PSU_UUID'], password=None)
        return user

    def get_user(self, userId):
        try:
            return User.objects.get(pk=userId)
        except User.DoesNotExist:
            return None
        
# This class manages the login if the user forgot their password.
class ForgotPasswordBackend(object):
    def authenticate(self, request, psu_uuid=None):
        if not psu_uuid:
            return None
        
        # We got here by decrypting a cryptographically-signed token. We assume the psu_uuid is valid.
        # TODO: Might want to check it just to be sure, but low-priority.
        
        request.session['identity'] = identity_from_psu_uuid(psu_uuid)
        logger.debug("service=myinfo psu_uuid=" + psu_uuid + " authenticate=passwordreset")

        try:
            user = User.objects.get(username = psu_uuid)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(psu_uuid, password=None)
        return user
    
    def get_user(self, userId):
        try:
            return User.objects.get(pk=userId)
        except User.DoesNotExist:
            return None