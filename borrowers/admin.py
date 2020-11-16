from django.contrib import admin

# Register your models here.
from borrowers.models import Borrower, BorrowerGroup, BorrowerBankAccount


@admin.register(Borrower)
class BorrowersAdmin(admin.ModelAdmin):
    list_display = (
        'registered_to', 'first_name', 'last_name', 'gender', 'phone', 'unique_identifier', 'account_number')
    list_display_links = ('registered_to', 'first_name', 'account_number')
    list_editable = ('phone', 'unique_identifier')
    prepopulated_fields = {'slug': ('first_name', 'last_name', 'phone', 'unique_identifier')}
    search_fields = ('first_name', 'last_name', 'unique_identifier', 'account_number')
    readonly_fields = ('image_tag',)
    list_filter = ('unique_identifier', 'slug', 'phone')

    class Meta:
        model = Borrower


@admin.register(BorrowerGroup)
class BorrowersGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_leader', 'collector', 'color_code', 'timestamp', 'updated')
    list_display_links = ('name',)
    list_editable = ('group_leader', 'collector')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'color_code')
    list_filter = ('name', 'slug')

    class Meta:
        model = BorrowerGroup


@admin.register(BorrowerBankAccount)
class BorrowerBankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'company', 'borrower', 'account_type', 'account_no', 'active', 'balance', 'interest_start_date',
        'initial_deposit_date')
    list_display_links = ('company', 'account_type')
    list_editable = ('balance', 'interest_start_date', 'initial_deposit_date')
    search_fields = ('account_type', 'account_no')
    list_filter = ('account_type', 'account_no')

    class Meta:
        model = BorrowerBankAccount
