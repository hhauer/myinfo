__author__ = 'Justin McClure'

from django.test import TestCase
from django.contrib.auth import get_user_model

from MyInfo.forms import SetOdinPasswordForm, ChangeOdinPasswordForm, ContactInformationForm, DirectoryInformationForm
from MyInfo.models import DirectoryInformation
from AccountPickup.models import OAMStatusTracker


class NewPasswordTestCase(TestCase):
    fixtures = ['MyInfo_views_test_data.json']

    def test_matched_passwords(self):
        confirm = new = "Password1!"
        mismatch = "Password2!"
        bad = "BadPass1"
        data = {}
        (user, _) = get_user_model().objects.get_or_create(username="111111111")

        # Test no data given
        f = SetOdinPasswordForm(user=user, data=data)
        self.assertFalse(f.is_valid())
        self.assertIn('new_password1', f.errors)
        self.assertIn('new_password2', f.errors)

        # Test incomplete data
        data['new_password1'] = new
        f = SetOdinPasswordForm(user=user, data=data)
        self.assertFalse(f.is_valid())
        self.assertNotIn('new_password1', f.errors)
        self.assertIn('new_password1', f.cleaned_data)
        self.assertIn('new_password2', f.errors)

        # Test non-matching data
        data['new_password2'] = mismatch
        f = SetOdinPasswordForm(user=user, data=data)
        self.assertFalse(f.is_valid())
        self.assertNotIn('new_password1', f.errors)
        self.assertIn('new_password1', f.cleaned_data)
        self.assertIn('new_password2', f.errors)

        # Test IIQ rejection
        data['new_password1'] = bad
        data['new_password2'] = bad
        f = SetOdinPasswordForm(user=user, data=data)
        self.assertFalse(f.is_valid())
        self.assertNotIn('new_password1', f.errors)
        self.assertNotIn('new_password2', f.errors)
        self.assertIn('__all__', f.errors)

        # Test good values
        data['new_password1'] = new
        data['new_password2'] = confirm
        password = user.password
        f = SetOdinPasswordForm(user=user, data=data)
        self.assertTrue(f.is_valid())
        self.assertIn('new_password1', f.cleaned_data)
        self.assertIn('new_password2', f.cleaned_data)
        # Make sure save doesn't store usable passwords in user
        self.assertFalse(f.user.has_usable_password())
        # Make sure password hash has changed
        self.assertNotEqual(password, user.password)


class PasswordChangeTestCase(TestCase):
    fixtures = ['MyInfo_views_test_data.json']

    def test_init(self):

        (user, _) = get_user_model().objects.get_or_create(username="111111111")

        # Test missing current
        data = {'new_password2': 'Password1', 'new_password1': 'Password1'}
        f = ChangeOdinPasswordForm(user=user, data=data)
        self.assertFalse(f.is_valid())
        self.assertIn('current_password', f.errors)

        # Test bad current for IIQ rejection
        data['current_password'] = 'BadPass1'
        f = ChangeOdinPasswordForm(user=user, data=data)
        self.assertFalse(f.is_valid())
        self.assertNotIn('new_password1', f.errors)
        self.assertNotIn('new_password2', f.errors)
        self.assertNotIn('current_password', f.errors)
        self.assertIn('__all__', f.errors)

        # Test good data
        data['current_password'] = 'Password2'
        f = ChangeOdinPasswordForm(user=user, data=data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.fields.popitem(last=False)[0], 'current_password')


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


class DirectoryInformationTestCase(TestCase):

    psu_uuid = "123456789"

    def test_good_init(self):
        # Test successful init without data
        form = DirectoryInformationForm(self.psu_uuid)
        self.assertNotIn("psu_uuid", form.fields)
        self.assertFalse(form.is_valid())
        # Test init with data
        (directory_information, _) = DirectoryInformation.objects.get_or_create(psu_uuid=self.psu_uuid)
        data = {'job_title': 'Django tester'}
        form = DirectoryInformationForm(self.psu_uuid, data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['job_title'], "Django tester")

    def test_bad_init(self):
        # Test init with no uuid
        self.assertRaises(TypeError, DirectoryInformationForm)

    def test_save(self):

        (oam_status, _) = OAMStatusTracker.objects.get_or_create(psu_uuid=self.psu_uuid)
        self.assertFalse(oam_status.set_directory)

        (directory_information, _) = DirectoryInformation.objects.get_or_create(psu_uuid=self.psu_uuid)
        self.assertIsNone(directory_information.job_title)
        form = DirectoryInformationForm(psu_uuid=self.psu_uuid, data={"job_title": 'Foo Bar'},
                                        instance=directory_information)
        self.assertTrue(form.is_valid())
        form.save()
        oam_status.refresh_from_db()
        self.assertTrue(oam_status.set_directory)
        directory_information.refresh_from_db()
        self.assertEqual(directory_information.job_title, "Foo Bar")