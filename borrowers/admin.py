from django.contrib import admin

# Register your models here.
from borrowers.models import Borrower, BorrowerGroup


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
    list_display = ('name', 'group_leader', 'collector', 'meeting_schedule', 'timestamp', 'updated')
    list_display_links = ('name',)
    list_editable = ('group_leader', 'collector', 'meeting_schedule')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('name', 'slug')

    class Meta:
        model = BorrowerGroup
