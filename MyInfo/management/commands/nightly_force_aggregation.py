__author__ = 'hhauer'

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

import cx_Oracle


class Command(BaseCommand):
    def handle(self, *args, **options):
        # For making the logs easier to interpret later, log out when we started.
        self.stdout.write("Nightly Force Aggregation started at: " + datetime.now())

        # Get banner connection settings.
        banner = settings.ORACLE_MANAGEMENT['banner']

        oracle_dsn = cx_Oracle.makedsn(banner['HOST'], banner['PORT'], banner['SID'])
        oracle_connection = cx_Oracle.Connection(banner['USER'], banner['PASS'], oracle_dsn)

        read_cursor = oracle_connection.cursor()
        read_cursor.execute(settings.ORACLE_MANAGEMENT['nightly_force']['EXPIRE_SQL'])

        write_cursor = oracle_connection.cursor()
        write_cursor.prepare(settings.ORACLE_MANAGEMENT['nightly_force']['INSERT_SQL'])
        write_cursor.setinputsizes(udc_id=225)

        for record in read_cursor:
            udc_id = record[0];

            self.stdout.write("Adding forced delta record for: " + udc_id)
            write_cursor.execute(None, {'udc_id': udc_id})

        oracle_connection.commit()

        # Finally, print out when we finished.
        self.stdout.write("Nightly Force Aggregation finished at: " + datetime.now())