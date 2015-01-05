"""CAS authentication backend"""
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.parse import urljoin
import urllib.request, urllib.error, urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model

from django_cas.models import User

from lib.api_calls import identity_from_psu_uuid

__all__ = ['CASBackend']

import logging
logger = logging.getLogger(__name__)

def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'validate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip(), None
        else:
            return None, None
    finally:
        page.close()


def _verify_cas2(ticket, service):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns username on success and None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            return tree[0][0].text, None
        else:
            return None, None
    finally:
        page.close()

def _verify_cas3(ticket, service):
    """Verifies CAS 3.0+ XML-based authentication ticket and returns extended attributes.

    Returns username on success and None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        user = None
        attributes = {}
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            for element in tree[0]:
                if element.tag.endswith('user'):
                    user = element.text
                elif element.tag.endswith('attributes'):
                    for attribute in element:
                        attributes[attribute.tag.split("}").pop()] = attribute.text
        return user, attributes
    finally:
        page.close()

def get_saml_assertion(ticket):
    return bytes("""<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Header/><SOAP-ENV:Body><samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"  MajorVersion="1" MinorVersion="1" RequestID="_192.168.16.51.1024506224022" IssueInstant="2002-06-19T17:03:44.022Z"><samlp:AssertionArtifact>""" + ticket + """</samlp:AssertionArtifact></samlp:Request></SOAP-ENV:Body></SOAP-ENV:Envelope>""", 'utf-8')

SAML_1_0_NS = 'urn:oasis:names:tc:SAML:1.0:'
SAML_1_0_PROTOCOL_NS = '{' + SAML_1_0_NS + 'protocol' + '}'
SAML_1_0_ASSERTION_NS = '{' + SAML_1_0_NS + 'assertion' + '}'

def _verify_cas2_saml(ticket, service):
    """Verifies CAS 3.0+ XML-based authentication ticket and returns extended attributes.

    @date: 2011-11-30
    @author: Carlos Gonzalez Vila <carlewis@gmail.com>

    Returns username and attributes on success and None,None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    # We do the SAML validation
    headers = {'soapaction': 'http://www.oasis-open.org/committees/security',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'accept': 'text/xml',
        'connection': 'keep-alive',
        'content-type': 'text/xml'}
    params = {'TARGET': service}
    url = urllib.request.Request(urljoin(settings.CAS_SERVER_URL, 'samlValidate') + '?' + urlencode(params), get_saml_assertion(ticket), headers)
    # url.data = get_saml_assertion(ticket)

    page = urllib.request.urlopen(url)

    try:
        user = None
        attributes = {}
        response = page.read()

        logger.debug("Received the following CAS2_SAML response: %s", response)

        tree = ElementTree.fromstring(response)
        # Find the authentication status
        success = tree.find('.//' + SAML_1_0_PROTOCOL_NS + 'StatusCode')
        if success is not None and success.attrib['Value'] == 'saml1p:Success':
            # User is validated
            attrs = tree.findall('.//' + SAML_1_0_ASSERTION_NS + 'Attribute')
            for at in attrs:
                if 'UID' in list(at.attrib.values()):
                    user = at.find(SAML_1_0_ASSERTION_NS + 'AttributeValue').text
                    attributes['UID'] = user
                values = at.findall(SAML_1_0_ASSERTION_NS + 'AttributeValue')
                if len(values) > 1:
                    values_array = []
                    for v in values:
                        values_array.append(v.text)
                    attributes[at.attrib['AttributeName']] = values_array
                else:
                    attributes[at.attrib['AttributeName']] = values[0].text
            logger.debug("Before returning from _verify user: %s", user)
            logger.debug("Before returning from _verify attributes: %s", attributes)
        else:
            logger.debug("CAS2 SAML was not successfully verified, success code is: %s", success.attrib['Value'])

        return user, attributes
    finally:
        page.close()


_PROTOCOLS = {'1': _verify_cas1, '2': _verify_cas2, '3': _verify_cas3, 'CAS_2_SAML_1_0': _verify_cas2_saml}


if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


class CASBackend(object):
    """CAS authentication backend"""

    def authenticate(self, ticket, service, request):
        """Verifies CAS ticket and gets or creates User object"""
        User = get_user_model()  # Custom user model.

        username, attributes = _verify(ticket, service)

        logger.debug("CAS Backend provided username: %s", username)
        logger.debug("CAS Backend provided attributes: %s", attributes)

        if not attributes or not username:
            return None

        if "PSUUUID" not in attributes:
            logger.error("Attributes were returned from CAS but did not include PSUUUID for username: " + username)
            return None

        psu_uuid = attributes['PSUUUID']

        request.session['attributes'] = attributes
        request.session['identity'] = identity_from_psu_uuid(psu_uuid)

        try:
            user = User.objects.get(username=psu_uuid)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(psu_uuid, password=None)
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
