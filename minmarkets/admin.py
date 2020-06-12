from django.contrib import admin

# Register your models here.
from minmarkets.models import LoanPackage, LoanCalculators, LoanCollectionPackage


@admin.register(LoanPackage)
class LoanPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'premium_package', 'package_owner', 'product_code', 'timestamp', 'updated')
    list_display_links = ('name', 'timestamp', 'product_code',)
    search_fields = ('name', 'product_code',)
    readonly_fields = ('image_tag',)
    list_filter = ('name', 'price', 'premium_package', 'package_owner', 'product_code',)


@admin.register(LoanCalculators)
class LoanCalculatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'premium_package', 'package_owner', 'product_code', 'timestamp', 'updated')
    list_display_links = ('name', 'timestamp', 'product_code',)
    search_fields = ('name', 'product_code',)
    readonly_fields = ('image_tag',)
    list_filter = ('name', 'price', 'premium_package', 'package_owner', 'product_code',)


@admin.register(LoanCollectionPackage)
class LoanCollectionPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'premium_package', 'package_owner', 'product_code', 'timestamp', 'updated')
    list_display_links = ('name', 'timestamp', 'product_code',)
    search_fields = ('name', 'product_code',)
    readonly_fields = ('image_tag',)
    list_filter = ('name', 'price', 'premium_package', 'package_owner', 'product_code',)