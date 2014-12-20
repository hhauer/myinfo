__author__ = 'hhauer'

import requests
import cx_Oracle


from django.core.management.base import BaseCommand, CommandError
from MyInfo.models import ContactInformation


class Command(BaseCommand):
    oracle_user = ''
    oracle_pass = ''

    oracle_host = ''
    oracle_port = ''
    oracle_sid = ''

    oracle_sql = ''

    iiq_host = ''
    iiq_user = ''
    iiq_pass = ''

    def get_iiq_url(self, udc_id):
        url = "https://{}/identityiq/rest/custom/getUUID/{}".format(self.iiq_host, udc_id)
        # self.stdout.write("URL: " + url)
        return url

    def handle(self, *args, **options):
        oracle_dsn = cx_Oracle.makedsn(self.oracle_host, self.oracle_port, self.oracle_sid)

        oracle_connection = cx_Oracle.Connection(self.oracle_user, self.oracle_pass, oracle_dsn)
        oracle_cursor = oracle_connection.cursor()

        oracle_cursor.execute(self.oracle_sql)

        for record in oracle_cursor:
            # UDC_ID, Phone, Email. Phone or email can be None.
            r = requests.get(self.get_iiq_url(record[0]),
                                    auth=(self.iiq_user, self.iiq_pass),
                                    verify=False)

            psu_uuid = r.json()

            if psu_uuid is None:
                self.stdout.write("No PSU_UUID was available for UDC_ID: " + record[0])
            else:
                obj, created = ContactInformation.objects.update_or_create(
                    psu_uuid = psu_uuid,
                    cell_phone = record[1],
                    alternate_email = record[2],
                )

                obj.save()




