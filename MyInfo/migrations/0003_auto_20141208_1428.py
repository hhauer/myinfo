# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyInfo', '0002_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directoryinformation',
            name='office_room',
            field=models.CharField(blank=True, null=True, max_length=10),
            preserve_default=True,
        ),
    ]
