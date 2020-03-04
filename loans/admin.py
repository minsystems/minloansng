from django.contrib import admin

# Register your models here.
from loans.models import LoanType, Collateral, LoanTerms, Loan, ModeOfRepayments, Penalty, CollateralFiles


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


admin.site.register(LoanTerms)
admin.site.register(Loan)
admin.site.register(ModeOfRepayments)
admin.site.register(Penalty)
admin.site.register(CollateralFiles)