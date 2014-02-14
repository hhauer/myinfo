from django.db import models

import logging
logger = logging.getLogger(__name__)

class OAMStatusTracker(models.Model):
    psu_uuid = models.CharField(unique=True, max_length=36, primary_key=True)
    
    select_names = models.BooleanField(default=False)
    set_contact_info = models.BooleanField(default=False)
    set_password = models.BooleanField(default=False)
    set_directory = models.BooleanField(default=False)
    provisioned = models.BooleanField(default=False)
    
    welcome_displayed = models.BooleanField(default=False)
    
    # Set to the time they last agreed to the AUP/Documents
    agree_aup = models.DateField(blank=True, null=True)