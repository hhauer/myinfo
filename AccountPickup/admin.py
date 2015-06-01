from django.contrib import admin
from AccountPickup.models import OAMStatusTracker


class OAMStatusTrackerAdmin(admin.ModelAdmin):
    search_fields = ['^psu_uuid']
    list_display = ['psu_uuid', 'select_odin_username', 'select_email_alias', 'set_contact_info', 'set_password',
                    'set_directory', 'provisioned', 'welcome_displayed', 'agree_aup', ]


admin.site.register(OAMStatusTracker, OAMStatusTrackerAdmin)