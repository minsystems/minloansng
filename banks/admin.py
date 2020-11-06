from django.contrib import admin


# Register your models here.
from banks.models import BankCode


@admin.register(BankCode)
class BankCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'otp_enabled', 'timestamp', 'updated')
    list_display_links = ('name',)
    list_editable = ('otp_enabled',)
    search_fields = ('name',)

    class Meta:
        model = BankCode
