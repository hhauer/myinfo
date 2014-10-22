# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.core.validators
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('psu_uuid', models.CharField(max_length=36, unique=True, serialize=False, primary_key=True)),
                ('cell_phone', localflavor.us.models.PhoneNumberField(blank=True, max_length=20, null=True)),
                ('alternate_email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='Mailcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='DirectoryInformation',
            fields=[
                ('psu_uuid', models.CharField(max_length=36, unique=True, serialize=False, primary_key=True)),
                ('company', models.CharField(blank=True, max_length=50, null=True, default='Portland State University', choices=[('Portland State University', 'Portland State University'), ('Portland State University Foundation', 'PSU Foundation')])),
                ('telephone', models.CharField(blank=True, max_length=32, validators=[django.core.validators.RegexValidator(re.compile('^[\\d\\-x ]*$', 32), 'Phone numbers may only contain numbers, spaces, or the characters - and x')], null=True)),
                ('fax', models.CharField(blank=True, max_length=32, validators=[django.core.validators.RegexValidator(re.compile('^[\\d\\-x ]*$', 32), 'Phone numbers may only contain numbers, spaces, or the characters - and x')], null=True)),
                ('job_title', models.CharField(blank=True, max_length=255, null=True)),
                ('office_room', models.CharField(blank=True, max_length=50, null=True)),
                ('street_address', models.CharField(blank=True, max_length=150, default='1825 SW Broadway', null=True)),
                ('city', models.CharField(blank=True, max_length=50, default='Portland', null=True)),
                ('state', localflavor.us.models.USStateField(blank=True, max_length=2, null=True, default='OR', choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AS', 'American Samoa'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('AA', 'Armed Forces Americas'), ('AE', 'Armed Forces Europe'), ('AP', 'Armed Forces Pacific'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('GU', 'Guam'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('MP', 'Northern Mariana Islands'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VI', 'Virgin Islands'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')])),
                ('zip_code', models.CharField(blank=True, max_length=10, default='97201', null=True)),
                ('department', models.ForeignKey(blank=True, null=True, to='MyInfo.Department')),
                ('mail_code', models.ForeignKey(blank=True, null=True, to='MyInfo.Mailcode')),
                ('office_building', models.ForeignKey(blank=True, null=True, to='MyInfo.Building')),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='MaintenanceNotice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('start_display', models.DateTimeField()),
                ('end_display', models.DateTimeField()),
                ('message', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
