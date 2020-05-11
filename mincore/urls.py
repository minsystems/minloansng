from django.urls import path

from mincore.views import SubscriberProcessor, MessageList, MessageDetail, AccountUpgrade, ContactProcessor, \
    AddStaffProcessor, SupportTicketProcessor

urlpatterns = [
    path('mailing-list/', SubscriberProcessor.as_view(), name='newsletter-processor'),
    path('contact-processor/', ContactProcessor.as_view(), name='contact-processor'),
    path('add-staff-processor/', AddStaffProcessor.as_view(), name='add-staff'),
    path('support-ticket-processor/', SupportTicketProcessor.as_view(), name='support-ticket'),
    path('account-upgrade/', AccountUpgrade.as_view(), name='account-upgrade'),
    path('<slug:slug>/messages/', MessageList.as_view(), name='message-list'),
    path('<slug:slug>/messages/<slug:slug_message>/detail/', MessageDetail.as_view(), name='message-detail'),
]