__author__ = 'Justin McClure'

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from random import choice
from MyInfo.models import MaintenanceNotice, Department
from MyInfo.forms import formPasswordChange, formNewPassword
from datetime import datetime, timedelta


class MyInfoViewsTestCase(TestCase):
    fixtures = ['MyInfo_views_test_data.json']

    def setUp(self):
        super(MyInfoViewsTestCase, self).setUp()
        self.HOST = 'testserver'
        self.INDEX = reverse('index')
        self.PICK = reverse('MyInfo:pick_action')
        self.PASSWORD = reverse('MyInfo:set_password')
        self.DIRECTORY = reverse('MyInfo:set_directory')
        self.CONTACT = reverse('MyInfo:set_contact')
        self.WELCOME = reverse('MyInfo:welcome_landing')
        self.PING = reverse('MyInfo:MyInfo.views.ping')
        self.NEXT = reverse("AccountPickup:next_step")
        self.RAND_IP = ["127.0.0." + str(i) for i in range(1, 256)]


class IndexTestCase(MyInfoViewsTestCase):

    def test_index_get(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.get(self.INDEX)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context['form'].is_bound)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(0, len(r.context['notices']))

    def test_index_get_maintenance(self):
        _ = MaintenanceNotice.objects.create(
            start_display=datetime.now(),
            end_display=datetime.now() + timedelta(days=1)
        )
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.get(self.INDEX)
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(0, len(r.context['notices']))
        MaintenanceNotice.objects.filter().delete()

    def test_index_get_future_maintenance(self):
        _ = MaintenanceNotice.objects.create(
            start_display=datetime.now() + timedelta(days=1),
            end_display=datetime.now() + timedelta(days=2)
        )
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.get(self.INDEX)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(0, len(r.context['notices']))
        MaintenanceNotice.objects.filter().delete()

    def test_index_get_past_maintenance(self):
        _ = MaintenanceNotice.objects.create(
            start_display=datetime.now() - timedelta(days=2),
            end_display=datetime.now() - timedelta(days=1)
        )
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.get(self.INDEX)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(0, len(r.context['notices']))
        MaintenanceNotice.objects.filter().delete()

    def test_index_post_bad(self):
        # test bad form input
        form = {'password': 'Password1!'}
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.post(self.INDEX, data=form)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())
        self.assertIn('error', r.context)
        self.assertEqual(r.context['error'], '')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test known bad user stub
        form['username'] = '000000000'
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.post(self.INDEX, data=form)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertTrue(r.context['form'].is_valid())
        self.assertIn('error', r.context)
        self.assertNotEqual(r.context['error'], '')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test good stub
        form['username'] = '123456789'
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        r = self.client.post(self.INDEX, data=form)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)


class PickActionTestCase(MyInfoViewsTestCase):

    def test_pick(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'username': '111111111', 'password': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.PICK, host=self.HOST)


class ChangePasswordTestCase(MyInfoViewsTestCase):

    def setUp(self):
        super(ChangePasswordTestCase, self).setUp()
        # Set up client to spoof random IP from list
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        # Log in pre-created user
        data = {'username': '111111111', 'password': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.PICK, host=self.HOST)

    def test_change_password_get(self):
        # Test get
        r = self.client.get(self.PASSWORD)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)
        self.assertIsInstance(r.context['form'], formPasswordChange)
        self.assertIn('success', r.context)
        self.assertFalse(r.context['success'])
        self.assertIn('error', r.context)
        self.assertIsNone(r.context['error'])

    def test_change_password_post(self):
        # Test invalid form
        r = self.client.post(self.PASSWORD, data={'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())

        # Test rejected new password
        r = self.client.post(self.PASSWORD, data={
            'newPassword': 'BadPass1',
            'confirmPassword': 'BadPass1',
            'currentPassword': 'Password1'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertTrue(r.context['form'].is_valid())
        self.assertIn('success', r.context)
        self.assertFalse(r.context['success'])
        self.assertIn('error', r.context)
        self.assertIsNotNone(r.context['error'])

        # Test rejected current password
        r = self.client.post(self.PASSWORD, data={
            'newPassword': 'Password1',
            'confirmPassword': 'Password1',
            'currentPassword': 'BadPass1'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertTrue(r.context['form'].is_valid())
        self.assertIn('success', r.context)
        self.assertFalse(r.context['success'])
        self.assertIn('error', r.context)
        self.assertIsNotNone(r.context['error'])

        # Test good input
        r = self.client.post(self.PASSWORD,
                             data={
                                 'newPassword': 'Password1',
                                 'confirmPassword': 'Password1',
                                 'currentPassword': 'Password2'},
                             follow=True)
        self.assertRedirects(r, self.PICK, host=self.HOST)


class NewPasswordTestCase(MyInfoViewsTestCase):

    def setUp(self):
        super(NewPasswordTestCase, self).setUp()
        # Set up client to spoof random IP from list
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        # Log in pre-created user
        data = {'username': '222222222', 'password': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.PASSWORD, host=self.HOST)

    def test_new_password_get(self):
        # Test get
        r = self.client.get(self.PASSWORD)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)
        self.assertNotIsInstance(r.context['form'], formPasswordChange)
        self.assertIsInstance(r.context['form'], formNewPassword)
        self.assertIn('success', r.context)
        self.assertFalse(r.context['success'])
        self.assertIn('error', r.context)
        self.assertIsNone(r.context['error'])

    def test_new_password_post(self):
        # Test invalid form
        r = self.client.post(self.PASSWORD, data={'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())

        # Test rejected new password
        r = self.client.post(self.PASSWORD, data={'newPassword': 'BadPass1', 'confirmPassword': 'BadPass1'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertTrue(r.context['form'].is_valid())
        self.assertIn('success', r.context)
        self.assertFalse(r.context['success'])
        self.assertIn('error', r.context)
        self.assertIsNotNone(r.context['error'])

        # Test good input
        data = {'newPassword': 'Password1', 'confirmPassword': 'Password1'}
        r = self.client.post(self.PASSWORD, data=data, follow=True)
        self.assertRedirects(r, self.PICK, host=self.HOST)


class SetDirectoryTestCase(MyInfoViewsTestCase):

    def setUp(self):
        super(SetDirectoryTestCase, self).setUp()
        # Set up client to spoof random IP from list
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        # Log in pre-created user
        data = {'username': '333333333', 'password': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.DIRECTORY, host=self.HOST)

    def test_set_directory_get(self):
        # Test get
        r = self.client.get(self.DIRECTORY)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)

    def test_set_directory_unpublished(self):
        c = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'username': '000000004', 'password': 'Password1'}
        _ = c.post(self.INDEX, data=data, follow=True)
        r = c.get(self.DIRECTORY)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        r = c.post(self.DIRECTORY, data={})
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)

    def test_set_directory_post(self):
        # Test invalid form
        r = self.client.post(self.DIRECTORY, data={'company': 'foo'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())

        # Test good input
        r = self.client.post(self.DIRECTORY, data={'company': 'Portland State University'})
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # Test status changed for forwarding
        r = self.client.get(self.NEXT)
        self.assertRedirects(r, self.PICK, host=self.HOST)


class SetContactTestCase(MyInfoViewsTestCase):

    def setUp(self):
        super(SetContactTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'username': '111111111', 'password': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.PICK, host=self.HOST)

    def test_contact_get(self):
        # Test get
        r = self.client.get(self.CONTACT)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)
        self.assertNotEqual(r.context['form'].initial, {})
        self.assertEqual(str(r.context['form'].instance), '111111111')

    def test_contact_post(self):
        # Test bad input
        r = self.client.post(self.CONTACT, {'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())

        # Test blank data
        r = self.client.post(self.CONTACT, {'alternate_email': None, 'cell_phone': None})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())

        # Test only one contact method input
        # * Only  email
        data = {'alternate_email': 'email@test.com'}
        r = self.client.post(self.CONTACT, data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # * * Is the data initially displayed on next visit?
        r = self.client.get(self.CONTACT)
        data2 = data
        data2['cell_phone'] = ''
        self.assertEqual(r.context['form'].initial, data2)
        # * Only Phone
        data = {'cell_phone': '503-867-5309'}
        r = self.client.post(self.CONTACT, data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # * * Is data showed as initial on next visit?
        r = self.client.get(self.CONTACT)
        data2 = data
        data2['alternate_email'] = ''
        self.assertEqual(r.context['form'].initial, data2)
        # Test full input
        data = {'alternate_email': 'email@test.com', 'cell_phone': '503-867-5309'}
        r = self.client.post(self.CONTACT, data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # * * Is data showed as initial on next visit?
        r = self.client.get(self.CONTACT)
        self.assertEqual(r.context['form'].initial, data)


class WelcomeTestCase(MyInfoViewsTestCase):

    def setUp(self):
        super(WelcomeTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'username': '111111111', 'password': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.PICK, host=self.HOST)

    def test_welcome(self):
        r = self.client.get(self.WELCOME)
        self.assertNotIn('identity', r.client.session)
        r = self.client.get(self.PICK, follow=True)
        redirect = self.INDEX + "?next=" + self.PICK
        self.assertRedirects(r, redirect, host=self.HOST)


class PingTestCase(MyInfoViewsTestCase):

        def test_ping(self):
            r = self.client.get(self.PING)
            self.assertEqual(r.content, b'Success')

            Department.objects.all().delete()

            r = self.client.get(self.PING)
            self.assertEqual(r.content, b'Database not available!')