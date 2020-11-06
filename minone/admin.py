from django.contrib import admin

from minone.models import MinOneDescription


# Register your models here.
@admin.register(MinOneDescription)
class MinoneModelAdmin(admin.ModelAdmin):
    list_display = ('maintenance_mode', 'price', 'key', 'timestamp', 'updated')
    list_display_links = ('key', 'timestamp', 'updated')
    list_editable = ('price',)
