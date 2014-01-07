from django.db import models
from localflavor.us.models import PhoneNumberField, USStateField

import logging
logger = logging.getLogger(__name__)

class MailCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.code

# For departmental dropdown choices.
class Department(models.Model):
    name = models.CharField(unique=True, max_length=50)
    
    def __unicode__(self):
        return self.name
    
# Directory information for users with psuPublish = y. Upstream logic assumes that
# all fields except psu_uuid are to be rendered and editable.
class DirectoryInformation(models.Model):
    COMPANY_CHOICES = (
        ('PSU', 'Portland State University'),
        ('PSUF', 'PSU Foundation'),
    )
    
    psu_uuid = models.CharField(unique=True, max_length=36, primary_key=True)
    
    company = models.CharField(max_length=4, choices=COMPANY_CHOICES, null=True, blank=True)
    
    telephone = PhoneNumberField(null=True, blank=True)
    fax = PhoneNumberField(null=True, blank=True)
    
    job_title = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    office_building = models.CharField(max_length=50, blank=True)
    office_room = models.CharField(max_length=50, blank=True)
    
    psu_mail_code = models.ForeignKey(MailCode, null=True, blank=True)
    street_address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = USStateField(blank=True, null=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    
    
    def __unicode__(self):
        return self.psu_uuid
    
# Password reset contact information.
class ContactInformation(models.Model):
    psu_uuid = models.CharField(unique=True, max_length=36, primary_key=True)
    
    cell_phone = PhoneNumberField(blank=True, null=True)
    alternate_email = models.EmailField(max_length=254, blank=True, null=True)
    
    
 
