from django.contrib import admin

# Register your models here.
from loans.models import LoanType, Collateral, LoanTerms, Loan, ModeOfRepayments, Penalty, CollateralFiles, \
    CollateralType


@admin.register(Collateral)
class CollateralAdmin(admin.ModelAdmin):
    list_display = ('collateral_type', 'name', 'registered_date', 'status', 'value', 'condition', 'collateral_files')
    list_display_links = ('collateral_type', 'name')
    list_editable = ('status',)
    list_filter = ('collateral_type', 'name', 'registered_date', 'status', 'condition')
    search_fields = ('name',)

    class Meta:
        model = Collateral


@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('package', 'timestamp', 'updated')
    list_display_links = ('package', 'timestamp')


class LoanAdmin(admin.ModelAdmin):
    list_display = ('account_officer', 'company', 'borrower', 'loan_type', 'loan_key', 'principal_amount', 'interest')
    list_display_links = ('account_officer', 'borrower')
    list_filter = ('loan_key', 'principal_amount')
    search_fields = ('loan_key', 'borrower')

    class Meta:
        model = Loan


admin.site.register(LoanTerms)
admin.site.register(Loan, LoanAdmin)
admin.site.register(ModeOfRepayments)
admin.site.register(Penalty)
admin.site.register(CollateralFiles)
admin.site.register(CollateralType)
