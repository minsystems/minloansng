from django.urls import path

from mincore.views import SubscriberProcessor, MessageList, MessageDetail, AccountUpgrade

urlpatterns = [
    path('mailing-list/', SubscriberProcessor.as_view(), name='newsletter-processor'),
    path('account-upgrade/', AccountUpgrade.as_view(), name='account-upgrade'),
    path('<slug:slug>/messages/', MessageList.as_view(), name='message-list'),
    path('<slug:slug>/messages/<slug:slug_message>/detail/', MessageDetail.as_view(), name='message-detail'),
]