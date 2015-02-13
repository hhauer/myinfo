from django.db import models


# Create your models here.
class Event(models.Model):
    EVENT_TYPES = (
        ('AUP Accepted', 'AUP Accepted'),
    )

    psu_uuid = models.CharField(max_length=36)
    spriden_id = models.CharField(max_length=32)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES)
    event_date = models.DateField()

    def __str__(self):
        return "[{}] for {}".format(self.event_type, self.psu_uuid)