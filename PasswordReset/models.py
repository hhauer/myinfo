from django.db import models
from random import randrange
from datetime import timedelta
from django.utils import timezone

# http://www.crockford.com/wrmg/base32.html
# Should reduce confusion on characters when typing in from a phone. No I/1 l/I l/1 confusion.
CHARSET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
LENGTH = 10

# This model is based largely on the model available at:
# https://github.com/workmajj/django-unique-random/
class TextMessageShortCode(models.Model):
    code = models.CharField(max_length = LENGTH)
    token = models.CharField(max_length = 256)
    
    created = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        
        # Delete old tokens first.
        TextMessageShortCode.objects.filter(created__lte = timezone.now() - timedelta(days=7)).delete()
        
        unique = False
        while not unique:
            new_code = ''
            for _ in range(LENGTH):
                new_code += CHARSET[randrange(0, len(CHARSET))]
            if not TextMessageShortCode.objects.filter(code = new_code):
                self.code = new_code
                unique = True
        
        super(TextMessageShortCode, self).save(*args, **kwargs)