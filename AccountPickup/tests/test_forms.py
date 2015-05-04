__author__ = "Justin McClure"
from importlib import import_module

from django.test import TestCase
from django.conf import settings

from AccountPickup.forms import OdinNameForm, EmailAliasForm
from AccountPickup.models import OAMStatusTracker
from lib.api_calls import APIException


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class OdinNameFormTestCase(TestCase):
    choices = ["Name 1 - Test1",
               "Name 2 - Test2", ]

    @classmethod
    def setUpTestData(cls):
        cls.session = SessionStore()
        cls.session['TRUENAME_USERNAMES'] = cls.choices
        cls.session.save()

    def test_good_init(self):
        # Test successful init without data
        form = OdinNameForm(self.session)
        self.assertEqual(form.fields['name'].label, "Odin Username")
        self.assertEqual([c for c in form.fields['name'].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])

        # Test init with data
        form = OdinNameForm(self.session, {"name": 1})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {"name": "1"})

    def test_bad_init(self):
        # Test init with no choices
        self.assertRaises(TypeError, OdinNameForm)
        # Test init with non-iterable choices
        self.assertRaises(TypeError, OdinNameForm, 42)

    def test_good_save(self):
        self.session['identity'] = {'PSU_UUID': '123456789'}
        self.session.modified = False

        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        self.assertFalse(oam_status.select_odin_username)
        self.assertNotIn('ODIN_NAME', self.session['identity'])
        self.assertNotIn('EMAIL_ADDRESS', self.session['identity'])

        form = OdinNameForm(self.session, {"name": 0})
        self.assertTrue(form.is_valid())
        form.save()

        oam_status.refresh_from_db()
        self.assertTrue(self.session.modified)
        self.assertTrue(oam_status.select_odin_username)
        self.assertIn('ODIN_NAME', self.session['identity'])
        self.assertIn('EMAIL_ADDRESS', self.session['identity'])

    def test_bad_save(self):
        self.session['identity'] = {'PSU_UUID': '000000002'}
        self.session.modified = False

        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        self.assertFalse(oam_status.select_odin_username)
        self.assertNotIn('ODIN_NAME', self.session['identity'])
        self.assertNotIn('EMAIL_ADDRESS', self.session['identity'])
        form = OdinNameForm(self.session, {"name": 0})
        self.assertTrue(form.is_valid())
        self.assertRaises(APIException, form.save)
        oam_status.refresh_from_db()
        self.assertFalse(self.session.modified)
        self.assertFalse(oam_status.select_odin_username)
        self.assertNotIn('ODIN_NAME', self.session['identity'])
        self.assertNotIn('EMAIL_ADDRESS', self.session['identity'])


class EmailAliasFormTestCase(TestCase):
    choices = ["None",
               "Name 1 - Test1",
               "Name 2 - Test2", ]

    @classmethod
    def setUpTestData(cls):
        cls.session = SessionStore()
        cls.session['TRUENAME_EMAILS'] = cls.choices
        cls.session.save()

    def test_good_init(self):
        # Test successful init without data
        form = EmailAliasForm(self.session)
        self.assertEqual(form.fields["alias"].label, "Email Alias")
        self.assertEqual([c for c in form.fields["alias"].choices], [
            (0, "None"), (1, "Name 1 - Test1"), (2, "Name 2 - Test2")])

        # Test init with data
        form = EmailAliasForm(self.session, {"alias": 1})
        self.assertEqual(form.fields["alias"].label, "Email Alias")
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {"alias": "1"})

    def test_bad_init(self):
        # Test init with no choices
        self.assertRaises(TypeError, EmailAliasForm)
        # Test init with non-iterable choices
        self.assertRaises(TypeError, EmailAliasForm, 42)

    def test_good_save(self):
        self.session['identity'] = {'PSU_UUID': '123456789'}
        self.session.modified = False
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        self.assertFalse(oam_status.select_email_alias)
        self.assertNotIn('EMAIL_ALIAS', self.session['identity'])
        form = EmailAliasForm(self.session, {"alias": 0})
        self.assertTrue(form.is_valid())
        form.save()
        oam_status.refresh_from_db()
        self.assertFalse(self.session.modified)
        self.assertTrue(oam_status.select_email_alias)
        self.assertNotIn('EMAIL_ALIAS', self.session['identity'])
        oam_status.select_email_alias = False
        oam_status.save()
        self.session.modified = False
        form = EmailAliasForm(self.session, {"alias": 1})
        self.assertTrue(form.is_valid())
        form.save()
        oam_status.refresh_from_db()
        self.assertTrue(self.session.modified)
        self.assertTrue(oam_status.select_email_alias)
        self.assertIn('EMAIL_ALIAS', self.session['identity'])

    def test_bad_save(self):
        self.session['identity'] = {'PSU_UUID': '000000002'}
        self.session.save()
        self.session.modified = False
        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        self.assertFalse(oam_status.select_email_alias)
        self.assertNotIn('EMAIL_ALIAS', self.session['identity'])
        form = EmailAliasForm(self.session, {"alias": 1})
        self.assertTrue(form.is_valid())
        self.assertRaises(APIException, form.save)
        oam_status.refresh_from_db()
        self.assertFalse(self.session.modified)
        self.assertFalse(oam_status.select_email_alias)
        self.assertNotIn('EMAIL_ALIAS', self.session['identity'])