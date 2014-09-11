from django.contrib import admin
from MyInfo.models import Department, Mailcode, Building, DirectoryInformation, ContactInformation, MaintenanceNotice

admin.site.register(Department)
admin.site.register(Mailcode)
admin.site.register(Building)
admin.site.register(DirectoryInformation)
admin.site.register(ContactInformation)
admin.site.register(MaintenanceNotice)
