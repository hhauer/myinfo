__author__ = 'Justin McClure'

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from random import choice


class AccountPickupViewsTestCase(TestCase):
    fixtures = ['AccountPickup_views_test_data.json']

    def setUp(self):
        super(AccountPickupViewsTestCase, self).setUp()
        self.HOST = 'testserver'
        self.INDEX = reverse('AccountPickup:index')
        self.AUP = reverse('AccountPickup:aup')
        self.ODIN = reverse('AccountPickup:odin')
        self.ALIAS = reverse('AccountPickup:alias')
        self.CONTACT = reverse('AccountPickup:contact_info')
        self.NEXT = reverse('AccountPickup:next_step')
        self.WAIT = reverse('AccountPickup:wait_for_provisioning')
        self.PROVISIONED = reverse('AccountPickup:provisioning_complete')
        self.RAND_IP = ["127.0.0." + str(i) for i in range(1, 256)]


class APIndexTestCase(AccountPickupViewsTestCase):

    def test_index_get(self):
        resp = self.client.get(self.INDEX)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context and not resp.context['form'].is_bound)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], '')

    def test_index_post(self):
        # test bad form input
        form = {'birth_date': '01/02/1903',
                'auth_pass': 'password1'}
        resp = self.client.post(self.INDEX, data=form)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context
                        and resp.context['form'].is_bound
                        and not resp.context['form'].is_valid())
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], '')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test known bad user stub
        form['id_number'] = '000000000'
        resp = self.client.post(self.INDEX, data=form)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context
                        and resp.context['form'].is_bound
                        and resp.context['form'].is_valid())
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.context['error'], 'That identity was not found.')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test good stub
        form['id_number'] = '123456789'
        resp = self.client.post(self.INDEX, data=form)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)


class APAupTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APAupTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '111111111', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, self.AUP, host=self.HOST)

    def test_aup_get(self):
        # Test get
        resp = self.client.get(self.AUP)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context and not resp.context['form'].is_bound)

    def test_aup_post(self):
        # Test bad input
        resp = self.client.post(self.AUP, {'accepted': False})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context and not resp.context['form'].is_valid())
        # Test good input
        resp = self.client.post(self.AUP, {'accepted': True})
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)
        # test forwarding for already completed
        resp = self.client.get(self.AUP)
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)


class APOdinTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APOdinTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '222222222', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, self.ODIN, host=self.HOST)

    def test_odin_get(self):
        # Test get
        resp = self.client.get(self.ODIN)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('odin_form' in resp.context and not resp.context['odin_form'].is_bound)

    def test_odin_post(self):
        # Test bad input
        resp = self.client.post(self.ODIN, {'name': '9001'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('odin_form' in resp.context
                        and resp.context['odin_form'].is_bound
                        and not resp.context['odin_form'].is_valid())

        # Test good input
        resp = self.client.post(self.ODIN, {'name': '1'})
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)
        # Test forwarding if already completed
        resp = self.client.get(self.ODIN)
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)


class APAliasTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APAliasTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '333333333', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, self.ALIAS, host=self.HOST)

    def test_alias_get(self):
        # Test get
        resp = self.client.get(self.ALIAS)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('mail_form' in resp.context and not resp.context['mail_form'].is_bound)

    def test_alias_post(self):
        # Test bad input
        resp = self.client.post(self.ALIAS, {'alias': '9001'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('mail_form' in resp.context
                        and resp.context['mail_form'].is_bound
                        and not resp.context['mail_form'].is_valid())

        # Test good input
        resp = self.client.post(self.ALIAS, {'alias': '1'})
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)
        # Test forwarding if step complete
        resp = self.client.get(self.ALIAS)
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)


class APContactTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APContactTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '444444444', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, self.CONTACT, host=self.HOST)

    def test_contact_get(self):
        # Test get
        resp = self.client.get(self.CONTACT)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context and not resp.context['form'].is_bound)

    def test_contact_post(self):
        # Test bad input
        resp = self.client.post(self.CONTACT, {'foo': 'bar'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context
                        and resp.context['form'].is_bound
                        and not resp.context['form'].is_valid())

        # Test good input
        data = {'alternate_email': 'email@test.com', 'cell_phone': '503-867-5309'}
        resp = self.client.post(self.CONTACT, data)
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)
        # Test forwarding if step complete
        resp = self.client.get(self.CONTACT)
        self.assertRedirects(resp, self.NEXT, target_status_code=302, host=self.HOST)


class APWaitTestCase(AccountPickupViewsTestCase):

    def test_wait(self):
        data = {'id_number': '555555555', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertRedirects(r, self.WAIT, host=self.HOST)
        r = self.client.post(self.WAIT, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # self.assertRedirects(r, self.NEXT, host=self.HOST)
        data['id_number'] = '999999999'
        _ = self.client.post(self.INDEX, data=data)
        r = self.client.post(self.WAIT, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)


class APNextTestCase(AccountPickupViewsTestCase):

    def test_next_directory(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '666666666', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, reverse('MyInfo:set_directory'), host=self.HOST)

    def test_next_password(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '777777777', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, reverse('MyInfo:set_password'), host=self.HOST)

    def test_next_welcome(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '888888888', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, reverse('MyInfo:welcome_landing'), host=self.HOST)

    def test_next_complete(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '999999999', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, reverse('MyInfo:pick_action'), host=self.HOST)