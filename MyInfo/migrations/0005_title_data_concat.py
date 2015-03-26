# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def truncate_job_title(apps, schema_editor):  # pragma: no cover
    directory = apps.get_model("MyInfo", "DirectoryInformation")
    for person in directory.objects.all():
        person.job_title = person.job_title[:128]
        person.save()


class Migration(migrations.Migration):  # pragma: no cover

    dependencies = [
        ('MyInfo', '0004_room_number_column_shrink'),
    ]

    operations = [
        migrations.RunPython(truncate_job_title),
    ]
