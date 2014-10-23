from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from CustomUser.models import PSUCustomUser

# Register your models here.
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = PSUCustomUser
        fields = ('psu_uuid', 'is_active', 'is_admin')


class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('psu_uuid', 'is_active', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('psu_uuid', 'is_active')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    search_fields = ('psu_uuid',)
    ordering = ('psu_uuid',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(PSUCustomUser, MyUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)