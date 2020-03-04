from django.urls import re_path, path

from .views import (
    AccountHomeView,
    AccountEmailActivateView,
    UserDetailUpdateView,
    ProfileDetailView
)

urlpatterns = [
    path('profile/<slug:slug>/', ProfileDetailView.as_view(), name='profile-detail'),
    re_path(r'^$', AccountHomeView.as_view(), name='home'),
    re_path(r'^details/$', UserDetailUpdateView.as_view(), name='user-update'),
    re_path(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', AccountEmailActivateView.as_view(), name='email-activate'),
    re_path(r'^email/resend-activation/$', AccountEmailActivateView.as_view(), name='resend-activation'),
]