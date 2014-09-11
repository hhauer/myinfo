from django.db import models
from localflavor.us.models import USStateField, PhoneNumberField

from MyInfo.validators import validate_psu_phone

import logging
logger = logging.getLogger(__name__)

# PSU Mailcode
class Mailcode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.code

# For departmental dropdown choices.
class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __unicode__(self):
        return self.name

# Buildings
class Building(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name
    
# Directory information for users with psuPublish = y. Upstream logic assumes that
# all fields except psu_uuid are to be rendered and editable.
class DirectoryInformation(models.Model):
    COMPANY_CHOICES = (
        ('Portland State University', 'Portland State University'),
        ('Portland State University Foundation', 'PSU Foundation'),
    )
    
    psu_uuid = models.CharField(unique=True, max_length=36, primary_key=True)
    
    company = models.CharField(max_length=50, choices=COMPANY_CHOICES, null=True, blank=True, default="Portland State University")
    
    telephone = models.CharField(max_length=32, null=True, blank=True, validators=[validate_psu_phone])
    fax = models.CharField(max_length=32, null=True, blank=True, validators=[validate_psu_phone])
    
    job_title = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    office_building = models.ForeignKey(Building, null=True, blank=True)
    office_room = models.CharField(max_length=50, null=True, blank=True)
    
    mail_code = models.ForeignKey(Mailcode, null=True, blank=True)
    street_address = models.CharField(max_length=150, null=True, blank=True, default="1825 SW Broadway")
    city = models.CharField(max_length=50, null=True, blank=True, default="Portland")
    state = USStateField(blank=True, null=True, default="OR")
    zip_code = models.CharField(max_length=10, null=True, blank=True, default="97201")
    
    
    def __unicode__(self):
        return self.psu_uuid
    
# Password reset contact information.
class ContactInformation(models.Model):
    psu_uuid = models.CharField(unique=True, max_length=36, primary_key=True)
    
    cell_phone = PhoneNumberField(blank=True, null=True)
    alternate_email = models.EmailField(max_length=254, blank=True, null=True)

    def __unicode__(self):
        return self.psu_uuid

# Maintenance notice.
class MaintenanceNotice(models.Model):
    start_display = models.DateTimeField()
    end_display = models.DateTimeField()

    message = models.TextField()

    def __str__(self):
        return "Maintenance starting: " + str(self.start_display)