from django.contrib import admin

# Register your models here.
from company.models import Company, Branch

admin.site.register(Branch)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'branch', 'active', 'timestamp')
    list_display_links = ('user', 'branch',)
    list_filter = ('user', 'branch', 'name', 'active',)
    search_fields = ('name', 'branch',)

    prepopulated_fields = {'slug': ('name', 'branch',)}

    ordering = ('-timestamp',)
