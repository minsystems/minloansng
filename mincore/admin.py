from django.contrib import admin

# Register your models here.
from mincore.models import Subscribers, Messages, SupportTickets


class SubscribersAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp', 'active',)
    list_display_links = ('email',)
    search_fields = ('email',)


admin.site.register(Subscribers, SubscribersAdmin)


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('to_obj', 'to_all', 'from_obj', 'title', 'content', 'active', 'timestamp')
    list_display_links = ('to_obj', 'title')
    search_fields = ('title', 'content', 'to_obj')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Messages, MessagesAdmin)


class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'ticket_id', 'affected_company', 'slug', 'completed', 'timestamp', 'updated')
    list_display_links = ('title', 'ticket_id')
    search_fields = ('title', 'content', 'ticket_id')
    prepopulated_fields = {'slug':('title', 'ticket_id')}


admin.site.register(SupportTickets, SupportTicketAdmin)
