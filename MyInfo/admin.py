from django.contrib import admin
from MyInfo.models import Department, MailCode, DirectoryInformation, ContactInformation

admin.site.register(Department)
admin.site.register(MailCode)
admin.site.register(DirectoryInformation)
admin.site.register(ContactInformation)