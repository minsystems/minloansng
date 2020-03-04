from django.contrib import admin


# Register your models here.
from banks.models import BankCode


@admin.register(BankCode)
class BankCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'timestamp', 'updated')
    list_display_links = ('name',)
    search_fields = ('name',)

    class Meta:
        model = BankCode
