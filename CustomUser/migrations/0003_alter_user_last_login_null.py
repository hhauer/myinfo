# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# Django 1.8 altered the AbstractBaseUser model's last_login field.
# Since our custom user subclasses that model, we need to migrate that too.
class Migration(migrations.Migration):

    dependencies = [
        ('CustomUser', '0002_auto_20141208_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='psucustomuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]
