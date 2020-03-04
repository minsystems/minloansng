from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import GuestEmail, EmailActivation, Profile

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin')
    list_filter = ('admin', 'staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('full_name', 'email', 'password')}),
        # ('Full name', {'fields': ()}),
        ('Permissions', {'fields': ('admin', 'staff', 'is_active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    search_fields = ('email', 'full_name',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ['email']

    class Meta:
        model = EmailActivation


admin.site.register(EmailActivation, EmailActivationAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium', 'phone', 'trial_days', 'plan', 'slug', 'token', 'updated')
    list_display_links = ('user',)
    list_filter = ('user', 'phone')
    readonly_fields = ('image_tag',)
    search_fields = ('user',)

    ordering = ('-timestamp',)
    fieldsets = (
        ('Basic Information', {'description': "Basic User Profile Information",
                               'fields': (('user',), 'image_tag', 'image', 'phone')}),
        ('Complete Full Information',
         {'classes': ('collapse',), 'fields': ('role', 'is_premium', 'trial_days', 'slug', 'plan', 'token')}),)


class GuestEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']

    class Meta:
        model = GuestEmail


admin.site.register(GuestEmail, GuestEmailAdmin)

admin.site.site_header = 'Minloansng, Minmarket, Minaccounts'
