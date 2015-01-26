# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def truncate_office_room(apps, schema_editor):  # pragma: no cover
    directory = apps.get_model("MyInfo", "DirectoryInformation")
    for person in directory.objects.all():
        person.office_room = person.office_room[:10]
        person.save()


class Migration(migrations.Migration):  # pragma: no cover

    dependencies = [
        ('MyInfo', '0002_initial_data'),
    ]

    operations = [
        migrations.RunPython(truncate_office_room),
    ]
