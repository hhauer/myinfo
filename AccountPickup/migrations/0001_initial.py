# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OAMStatusTracker',
            fields=[
                ('psu_uuid', models.CharField(max_length=36, unique=True, serialize=False, primary_key=True)),
                ('select_odin_username', models.BooleanField(default=False)),
                ('select_email_alias', models.BooleanField(default=False)),
                ('set_contact_info', models.BooleanField(default=False)),
                ('set_password', models.BooleanField(default=False)),
                ('set_directory', models.BooleanField(default=False)),
                ('provisioned', models.BooleanField(default=False)),
                ('welcome_displayed', models.BooleanField(default=False)),
                ('agree_aup', models.DateField(blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
