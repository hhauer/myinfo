__author__ = 'Justin McClure'

from django.test import TestCase
from MyInfo.forms import formNewPassword, formPasswordChange, ContactInformationForm


class NewPasswordTestCase(TestCase):
    def test_matched_passwords(self):
        confirm = new = "Password1!"
        bad = "Password2!"
        data = {}

        # Test no data given
        f = formNewPassword(data)
        self.assertFalse(f.is_valid())
        self.assertIn('newPassword', f.errors)
        self.assertIn('confirmPassword', f.errors)

        # Test incomplete data
        data['newPassword'] = new
        f = formNewPassword(data)
        self.assertFalse(f.is_valid())
        self.assertNotIn('newPassword', f.errors)
        self.assertIn('newPassword', f.cleaned_data)
        self.assertIn('confirmPassword', f.errors)

        # Test non-matching data
        data['confirmPassword'] = bad
        f = formNewPassword(data)
        self.assertFalse(f.is_valid())
        self.assertNotIn('newPassword', f.errors)
        self.assertIn('newPassword', f.cleaned_data)
        self.assertIn('confirmPassword', f.errors)

        # Test good values
        data['confirmPassword'] = confirm
        f = formNewPassword(data)
        self.assertTrue(f.is_valid())
        self.assertIn('newPassword', f.cleaned_data)
        self.assertIn('confirmPassword', f.cleaned_data)


class PasswordChangeTestCase(TestCase):
    def test_init(self):
        # Test missing current
        data = {'confirmPassword': 'foo', 'newPassword': 'foo'}
        f = formPasswordChange(data)
        self.assertFalse(f.is_valid())
        self.assertIn('currentPassword', f.errors)
        # Test good data
        data['currentPassword'] = 'bar'
        f = formPasswordChange(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.fields.popitem(last=False)[0], 'currentPassword')


class ContactInformationFormTestCase(TestCase):
    def test_no_data(self):
        f = ContactInformationForm({})
        self.assertFalse(f.is_valid())
        self.assertNotEqual(0, len(f.non_field_errors()))

    def test_bad_email(self):
        f = ContactInformationForm({'alternate_email': 'test@pdx.edu'})
        self.assertFalse(f.is_valid())
        self.assertIn('alternate_email', f.errors)

    def test_good_contact_info(self):
        # Just phone number
        data = {'cell_phone': '503-867-5309'}
        f = ContactInformationForm(data)
        self.assertTrue(f.is_valid())
        self.assertIn('cell_phone', f.cleaned_data)
        self.assertNotEqual(f.cleaned_data['cell_phone'], '')
        self.assertIn('alternate_email', f.cleaned_data)
        self.assertEqual(f.cleaned_data['alternate_email'], '')
        # Both
        data['alternate_email'] = 'test@email.com'
        f = ContactInformationForm(data)
        self.assertTrue(f.is_valid())
        self.assertIn('cell_phone', f.cleaned_data)
        self.assertNotEqual(f.cleaned_data['cell_phone'], '')
        self.assertIn('alternate_email', f.cleaned_data)
        self.assertNotEqual(f.cleaned_data['alternate_email'], '')