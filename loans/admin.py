from django.contrib import admin

# Register your models here.
from loans.models import LoanType, Collateral, LoanTerms, Loan, ModeOfRepayments, Penalty, CollateralFiles, \
    CollateralType, LoanActivityComments


@admin.register(LoanActivityComments)
class LoanActivityCommentsAdmin(admin.ModelAdmin):
    list_display = ("assigned_to", "done_by", "loan", "comment", "active", "timestamp")
    list_display_links = ("assigned_to", "loan")
    list_editable = ("active",)
    list_filter = ("assigned_to", "done_by", "loan", "timestamp", "active")
    search_fields = ("assigned_to", "done_by", "comment")


@admin.register(Collateral)
class CollateralAdmin(admin.ModelAdmin):
    list_display = ('slug', 'collateral_type', 'name', 'registered_date', 'status', 'value', 'condition', 'collateral_files')
    list_display_links = ('collateral_type', 'name', 'slug')
    list_editable = ('status',)
    list_filter = ('collateral_type', 'name', 'registered_date', 'status', 'condition')
    search_fields = ('name',)


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
