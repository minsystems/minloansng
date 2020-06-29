from django.contrib import admin

# Register your models here.
from company.models import Company, Branch, RemitaCredentials, RemitaMandateActivationData

admin.site.register(Branch)
admin.site.register(RemitaMandateActivationData)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'branch', 'active', 'timestamp')
    list_display_links = ('user', 'branch',)
    list_filter = ('user', 'branch', 'name', 'active',)
    search_fields = ('name', 'branch',)

    prepopulated_fields = {'slug': ('name', 'branch',)}

    ordering = ('-timestamp',)


@admin.register(RemitaCredentials)
class RemitaCredentialsAdmin(admin.ModelAdmin):
    list_display = ('connected_firm', 'merchantId', 'serviceTypeId', 'apiKey', 'mandateType')
    list_display_links = ('connected_firm', 'merchantId')
    list_filter = ('apiKey', 'merchantId')
    search_fields = ('merchantId', 'apiKey', 'serviceTypeId')
