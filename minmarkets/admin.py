from django.contrib import admin

# Register your models here.
from minmarkets.models import LoanPackage


@admin.register(LoanPackage)
class LoanPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'premium_package', 'package_owner', 'timestamp', 'updated')
    list_display_links = ('name', 'timestamp')
    search_fields = ('name',)
    readonly_fields = ('image_tag',)
    list_filter = ('name', 'price', 'premium_package', 'package_owner')