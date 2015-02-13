import requests

__author__ = 'hhauer'

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from AccountPickup.models import OAMStatusTracker
from ods_integration.models import Event


class Command(BaseCommand):
    def get_iiq_url(self, psu_uuid):
        url = "https://{}/identityiq/rest/custom/getSpriden/{}".format(settings.SAILPOINT_SERVER_URL, psu_uuid)
        return url

    def handle(self, *args, **options):
        # For making the logs easier to interpret later, log out when we started.
        self.stdout.write("Nightly Export AUP started at: {}".format(datetime.datetime.now()))

        # Truncate old data.
        self.stdout.write("Truncating old records. Count: " + str(Event.objects.count()));
        Event.objects.all().delete()

        # Get any oamstatustracker that updated their AUP yesterday.
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        aup_changes = OAMStatusTracker.objects.filter(agree_aup=yesterday)

        for x in aup_changes:
            r = requests.get(
                self.get_iiq_url(x.psu_uuid),
                auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD),
                verify=False
            )

            spriden_id = r.json()

            if spriden_id is None or spriden_id == "" or spriden_id == "None":
                self.stdout.write("Error converting {} to spriden_id.".format(x.psu_uuid))
            else:
                Event.objects.create(psu_uuid=x.psu_uuid,
                                     spriden_id=spriden_id,
                                     event_type="AUP Accepted",
                                     event_date=yesterday)
                self.stdout.write("Created ODS event for " + x.psu_uuid)

        # Finally, print out when we finished.
        self.stdout.write("Nightly Export AUP finished at: {}".format(datetime.datetime.now()))