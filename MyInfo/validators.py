import re
from django.core.validators import RegexValidator


psu_phone_re = re.compile(r"^[\d\-x ]*$")
validate_psu_phone = RegexValidator(psu_phone_re,
        "Phone numbers may only contain numbers, spaces, or the characters - and x")
