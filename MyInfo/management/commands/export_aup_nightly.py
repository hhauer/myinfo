import requests

__author__ = 'hhauer'

import datetime
import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from AccountPickup.models import OAMStatusTracker


class Command(BaseCommand):
    def get_iiq_url(self, psu_uuid):
        url = "https://{}/identityiq/rest/custom/getSpriden/{}".format(settings.SAILPOINT_SERVER_URL, psu_uuid)
        return url

    def handle(self, *args, **options):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        # Come up with a reasonable filename.
        csv_filename = "aup_acceptance_{}.csv".format(yesterday.strftime("%Y%m%d"))

        # Get any oamstatustracker that updated their AUP yesterday.
        aup_changes = OAMStatusTracker.objects.filter(agree_aup=yesterday)

        with open(csv_filename, 'w') as file:
            csv_file = csv.writer(file, delimiter='|')

            for x in aup_changes:
                r = requests.get(
                    self.get_iiq_url(x.psu_uuid),
                    auth=(settings.SAILPOINT_USERNAME, settings.SAILPOINT_PASSWORD),
                    verify=False
                )

                spriden_id = r.json()
                row = [spriden_id, 'AUP Accepted', yesterday.strftime("%Y%m%d")]
                csv_file.writerow(row)