# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyInfo', '0005_title_data_concat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directoryinformation',
            name='job_title',
            field=models.CharField(blank=True, null=True, max_length=128),
            preserve_default=True,
        ),
    ]
