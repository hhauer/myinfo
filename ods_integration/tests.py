import datetime

from django.test import TestCase
from django.core.management import call_command

from AccountPickup.models import OAMStatusTracker
from ods_integration.models import Event


# Create your tests here.
class IntegrationTestCase(TestCase):
    def setUp(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        last_week = datetime.date.today() - datetime.timedelta(days=7)

        OAMStatusTracker.objects.create(psu_uuid="agree-today", agree_aup=datetime.date.today())
        OAMStatusTracker.objects.create(psu_uuid="agree-yesterday", agree_aup=yesterday)
        OAMStatusTracker.objects.create(psu_uuid="agree-last-week", agree_aup=last_week)

        # Call the management command we're testing.
        call_command('nightly_export_aup')

    def test_today_not_included(self):
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(psu_uuid="agree-today")

    def test_last_week_not_included(self):
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(psu_uuid="agree-last-week")

    def test_yesterday_included(self):
        events = Event.objects.all()

        self.assertQuerysetEqual(events, ['<Event: [AUP Accepted] for agree-yesterday>'])