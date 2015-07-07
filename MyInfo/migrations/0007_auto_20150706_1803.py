# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyInfo', '0006_title_column_shrink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directoryinformation',
            name='psu_uuid',
            field=models.CharField(unique=True, max_length=36, serialize=False, editable=False, primary_key=True),
        ),
    ]
