from django.contrib import admin

# Register your models here.
from company.models import Company, Branch, RemitaCredentials, RemitaMandateActivationData, \
    RemitaMandateTransactionRecord, RemitaPaymentDetails, RemitaMandateStatusReport, BankAccountType

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


class RemitaPaymentDetailsInline(admin.TabularInline):
    model = RemitaPaymentDetails


@admin.register(RemitaMandateTransactionRecord)
class RemitaMandateTransactionRecordAdmin(admin.ModelAdmin):
    list_display = ('loan', 'remita_dd_mandate_owned_record', 'total_transaction_count', 'total_amount')
    list_display_links = ('loan',)
    list_filter = ('loan', 'total_transaction_count', 'remita_dd_mandate_owned_record')
    inlines = [RemitaPaymentDetailsInline]


@admin.register(RemitaMandateStatusReport)
class RemitaMandateStatusReportAdmin(admin.ModelAdmin):
    list_display = ('loan', 'start_date', 'end_date', 'request_id', 'mandate_id', 'registration_date', 'mandate_status', 'report_status')
    list_display_links = ('start_date', 'mandate_id', 'report_status')
    list_editable = ('mandate_status',)
    list_filter = ('mandate_id', 'request_id')
    search_fields = ('loan', 'mandate_id', 'request_id')


@admin.register(BankAccountType)
class BankAccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'active', 'color_code', 'maximum_withdrawal_amount', 'annual_interest_rate', 'interest_calculation_per_year')
    list_display_links = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('company', 'name', 'color_code')
    prepopulated_fields = {'slug':('name', 'company')}