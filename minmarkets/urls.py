from django.urls import path

from minmarkets.views import WelcomeView

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
]
