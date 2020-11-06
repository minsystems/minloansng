from django.urls import path

from settings.api.views import CompanyStaffsAPIView

urlpatterns = [
    path('<slug:slug>/list/', CompanyStaffsAPIView.as_view(), name='company-staff-api'),
]