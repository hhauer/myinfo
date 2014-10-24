from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from CustomUser.models import PSUCustomUser

# Register your models here.
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = PSUCustomUser
        fields = ('username', 'is_active', 'is_admin')

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.HiddenInput, initial='!')
    password2 = forms.CharField(label='Password confirmation', widget=forms.HiddenInput, initial='!')

    class Meta:
        model = PSUCustomUser
        fields = ('username', 'is_active', 'is_admin')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_unusable_password()

        if commit:
            user.save()
        return user


class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'is_active', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('username', 'is_active')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(PSUCustomUser, MyUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)