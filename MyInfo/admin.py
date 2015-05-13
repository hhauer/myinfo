from django.contrib import admin
from MyInfo.models import Department, Mailcode, Building, DirectoryInformation, ContactInformation, MaintenanceNotice


class DirectoryInformationAdmin(admin.ModelAdmin):
    search_fields = ['^psu_uuid']
    list_display = ['psu_uuid', 'company', 'telephone', 'fax', 'job_title', 'department', 'office_building',
                    'office_room', 'mail_code', ]


class ContactInformationAdmin(admin.ModelAdmin):
    search_fields = ['^psu_uuid']
    list_display = ['psu_uuid', 'cell_phone', 'alternate_email', ]

admin.site.register(Department)
admin.site.register(Mailcode)
admin.site.register(Building)
admin.site.register(DirectoryInformation, DirectoryInformationAdmin)
admin.site.register(ContactInformation, ContactInformationAdmin)
admin.site.register(MaintenanceNotice)