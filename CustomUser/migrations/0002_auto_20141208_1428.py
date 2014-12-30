# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUser', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='psucustomuser',
            options={'verbose_name_plural': 'PSU Users', 'verbose_name': 'PSU User'},
        ),
    ]
