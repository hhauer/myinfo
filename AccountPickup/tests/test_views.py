__author__ = 'Justin McClure'

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from random import choice
from lib.api_calls import APIException


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
        self.RAND_IP = ["127.0.0." + str(i) for i in range(1, 256)]


class APIndexTestCase(AccountPickupViewsTestCase):

    def test_index_get(self):
        r = self.client.get(self.INDEX)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)
        self.assertIn('error', r.context)
        self.assertEqual(r.context['error'], '')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_index_post(self):
        # test bad form input
        form = {'birth_date': '01/02/1903', 'auth_pass': 'password1'}
        r = self.client.post(self.INDEX, data=form)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())
        self.assertIn('error', r.context)
        self.assertEqual(r.context['error'], '')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test known bad user stub
        form['id_number'] = '000000000'
        r = self.client.post(self.INDEX, data=form)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertTrue(r.context['form'].is_valid())
        self.assertIn('error', r.context)
        self.assertNotEqual(r.context['error'], '')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Test good stub
        form['id_number'] = '123456789'
        r = self.client.post(self.INDEX, data=form)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)

        # Test session flushing
        s = self.client.session.session_key
        _ = self.client.post(self.INDEX, data=form)
        self.assertNotEqual(self.client.session.session_key, s)


class APAupTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APAupTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '111111111', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.AUP, host=self.HOST)

    def test_aup_get(self):
        # Test get
        r = self.client.get(self.AUP)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)

    def test_aup_post(self):
        # Test bad input
        r = self.client.post(self.AUP, {'accepted': False})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())
        # Test good input
        r = self.client.post(self.AUP, {'accepted': True})
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # test forwarding for already completed
        r = self.client.get(self.AUP)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)


class APOdinTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APOdinTestCase, self).setUp()
        # Set up client to spoof random IP from list
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        # Log in pre-created user
        data = {'id_number': '222222222', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.ODIN, host=self.HOST)

    def test_odin_get(self):
        # Test get
        r = self.client.get(self.ODIN)
        self.assertEqual(r.status_code, 200)
        self.assertIn('odin_form', r.context)
        self.assertFalse(r.context['odin_form'].is_bound)

    def test_odin_post(self):
        # Test bad input
        r = self.client.post(self.ODIN, {'name': '9001'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('odin_form', r.context)
        self.assertTrue(r.context['odin_form'].is_bound)
        self.assertFalse(r.context['odin_form'].is_valid())

        # Test good input
        r = self.client.post(self.ODIN, {'name': '1'})
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # Test forwarding if already completed
        r = self.client.get(self.ODIN)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)

    def test_odin_api_fail(self):
        # Truename down
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '000000001', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        _ = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRaisesMessage(APIException, "Truename API call failed", self.client.get, self.ODIN)

        # IIQ down
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data['id_number'] = '000000002'
        _ = self.client.post(self.INDEX, data=data, follow=True)
        data = {'name': '0'}
        self.assertRaisesMessage(APIException, "IIQ API call failed", self.client.post, self.ODIN, data=data)


class APAliasTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APAliasTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '333333333', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.ALIAS, host=self.HOST)

    def test_alias_get(self):
        # Test get
        r = self.client.get(self.ALIAS)
        self.assertEqual(r.status_code, 200)
        self.assertIn('mail_form', r.context)
        self.assertFalse(r.context['mail_form'].is_bound)

    def test_alias_post(self):
        # Test bad input
        r = self.client.post(self.ALIAS, {'alias': '9001'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('mail_form', r.context)
        self.assertTrue(r.context['mail_form'].is_bound)
        self.assertFalse(r.context['mail_form'].is_valid())
        self.assertNotIn('EMAIL_ALIAS', self.client.session['identity'])

        # Test good input
        r = self.client.post(self.ALIAS, {'alias': '1'})
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        self.assertIn('EMAIL_ALIAS', self.client.session['identity'])
        # Test forwarding if step complete
        r = self.client.get(self.ALIAS)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)

        # Test 'No Alias' post
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '333333334', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.ALIAS, host=self.HOST)

        r = self.client.post(self.ALIAS, {'alias': '0'})
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        self.assertNotIn('EMAIL_ALIAS', self.client.session['identity'])
        # Test forwarding if step complete
        r = self.client.get(self.ALIAS)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)

    def test_alias_api_fail(self):
        # Truename down
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '000000001', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        _ = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRaises(APIException, self.client.get, self.ALIAS)

        # IIQ down
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data['id_number'] = '000000002'
        _ = self.client.post(self.INDEX, data=data, follow=True)
        data = {'alias': '1'}
        self.assertRaises(APIException, self.client.post, self.ALIAS, data=data)


class APContactTestCase(AccountPickupViewsTestCase):

    def setUp(self):
        super(APContactTestCase, self).setUp()
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '444444444', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.CONTACT, host=self.HOST)

    def test_contact_get(self):
        # Test get
        r = self.client.get(self.CONTACT)
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertFalse(r.context['form'].is_bound)

    def test_contact_post(self):
        # Test bad input
        r = self.client.post(self.CONTACT, {'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)
        self.assertTrue(r.context['form'].is_bound)
        self.assertFalse(r.context['form'].is_valid())

        # Test good input
        data = {'alternate_email': 'email@test.com', 'cell_phone': '503-867-5309'}
        r = self.client.post(self.CONTACT, data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # Test forwarding if step complete
        r = self.client.get(self.CONTACT)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)

        # Test only one contact method input
        # * Only  email
        # * * Login
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '444444445', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.CONTACT, host=self.HOST)
        # * * Post
        data = {'alternate_email': 'email@test.com'}
        r = self.client.post(self.CONTACT, data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # * * Test forwarding if step complete
        r = self.client.get(self.CONTACT)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # * Only Phone
        # * * Login
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '444444446', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.CONTACT, host=self.HOST)
        # * * Post
        data = {'cell_phone': '503-867-5309'}
        r = self.client.post(self.CONTACT, data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        # * * Test forwarding if step complete
        r = self.client.get(self.CONTACT)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)


class APWaitTestCase(AccountPickupViewsTestCase):
    # Note: Wait view will probably be removed in the future
    def test_wait(self):
        data = {'id_number': '555555555', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, self.WAIT, host=self.HOST)
        # _ = self.client.get(self.WAIT, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # self.assertRedirects(r, self.NEXT, host=self.HOST)
        # Test already provisioned
        data['id_number'] = '999999999'
        r = self.client.post(self.INDEX, data=data)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)
        r = self.client.get(self.WAIT)
        self.assertRedirects(r, self.NEXT, target_status_code=302, host=self.HOST)


class APNextTestCase(AccountPickupViewsTestCase):

    def test_next_directory(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '666666666', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, reverse('MyInfo:set_directory'), host=self.HOST)

    def test_next_password(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '777777777', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, reverse('MyInfo:set_password'), host=self.HOST)

    def test_next_welcome(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '888888888', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        # Welcome page should kill session
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(r, reverse('MyInfo:welcome_landing'), host=self.HOST)

    def test_next_complete(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '999999999', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        r = self.client.post(self.INDEX, data=data, follow=True)
        self.assertRedirects(r, reverse('MyInfo:pick_action'), host=self.HOST)

    def test_next_api_fail(self):
        self.client = Client(REMOTE_ADDR=choice(self.RAND_IP))
        data = {'id_number': '000000003', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        self.assertRaisesMessage(APIException, "IIQ API call failed",
                                 self.client.post, self.INDEX, data=data, follow=True)


class APRateLimitTestCase(AccountPickupViewsTestCase):

    def test_rate_limit(self):
        self.client = Client(REMOTE_ADDR="127.0.1.1")
        for _ in range(30):
            self.client.get(self.INDEX)
        r = self.client.get(self.INDEX, follow=True)
        self.assertListEqual(r.redirect_chain, [])

        data = {'id_number': '123456789', 'birth_date': '12/21/2012', 'auth_pass': 'Password1!'}
        for _ in range(30):
            self.client.post(self.INDEX, data)
        r = self.client.get(self.INDEX, follow=True)
        self.assertListEqual(r.redirect_chain, [])
        r = self.client.post(self.INDEX, data, follow=True)
        self.assertRedirects(r, reverse('rate_limited'), host=self.HOST)
