__author__ = "Justin McClure"
from importlib import import_module

from django.test import TestCase
from django.conf import settings

from AccountPickup.forms import OdinNameForm, EmailAliasForm
from AccountPickup.models import OAMStatusTracker


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class OdinNameFormTestCase(TestCase):
    choices = ["Name 1 - Test1",
               "Name 2 - Test2", ]

    def test_good_init(self):
        # Test successful init without data
        form = OdinNameForm(enumerate(self.choices))
        self.assertEqual(form.fields['name'].label, "Odin Username")
        self.assertEqual([c for c in form.fields['name'].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])

        # Test init with data
        form = OdinNameForm(enumerate(self.choices), {"name": 1})
        self.assertEqual(form.fields['name'].label, "Odin Username")
        self.assertEqual([c for c in form.fields['name'].choices], [(0, "Name 1 - Test1"), (1, "Name 2 - Test2")])
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {"name": "1"})

    def test_bad_init(self):
        # Test init with no choices
        self.assertRaises(TypeError, OdinNameForm)
        # Test init with non-iterable choices
        self.assertRaises(TypeError, OdinNameForm, 42)


class EmailAliasFormTestCase(TestCase):
    choices = ["None",
               "Name 1 - Test1",
               "Name 2 - Test2", ]
    session = SessionStore()
    session['TRUENAME_EMAILS'] = choices
    session['identity'] = {'PSU_UUID': '123456789'}
    session.modified = True
    session.save()

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

    def test_save(self):

        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.session['identity']['PSU_UUID'])
        self.assertFalse(oam_status.select_email_alias)
        self.assertNotIn('EMAIL_ALIAS', self.session['identity'])
        form = EmailAliasForm(self.session, {"alias": 0})
        self.assertTrue(form.is_valid())
        form.save()
        oam_status.refresh_from_db()
        self.assertTrue(oam_status.select_email_alias)
        self.assertNotIn('EMAIL_ALIAS', self.session['identity'])
        oam_status.select_email_alias = False
        oam_status.save()
        form = EmailAliasForm(self.session, {"alias": 1})
        self.assertTrue(form.is_valid())
        form.save()
        oam_status.refresh_from_db()
        self.assertTrue(oam_status.select_email_alias)
        self.assertIn('EMAIL_ALIAS', self.session['identity'])
