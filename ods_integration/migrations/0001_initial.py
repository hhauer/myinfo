# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('psu_uuid', models.CharField(max_length=36)),
                ('spriden_id', models.CharField(max_length=32)),
                ('event_type', models.CharField(max_length=32, choices=[('AUP Accepted', 'AUP Accepted')])),
                ('event_date', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
