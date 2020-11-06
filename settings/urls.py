from django.urls import path

from settings.views import CompanySettings

urlpatterns = [
    path('<slug:slug>/settings/', CompanySettings.as_view(), name='company-settings')
]
