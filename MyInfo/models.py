from django.db import models

import logging
logger = logging.getLogger(__name__)

# All data shared with sailpoint is stored via this model using a key/value pattern.
class UserDataItem(models.Model):
    psu_uuid = models.CharField(max_length=36)
    key_name = models.CharField(max_length=64)
    # 254 characters are necessary to handle all RFC3696/5321-compliant email addresses.
    key_valu = models.CharField(max_length=254, blank=True, null=True)
    
    date_created = models.DateField(auto_now_add = True)
    date_updated = models.DateField(auto_now = True)
 
# For departmental dropdown choices.
# http://stackoverflow.com/questions/749000/django-how-to-use-stored-model-instances-as-form-choices
class Department(models.Model):
    name = models.CharField(unique=True, max_length=50)
    
    def __unicode__(self):
        return self.name
    
class CellCarrier(models.Model):
    name = models.CharField(unique=True, max_length=50)
    
    def __unicode__(self):
        return self.name