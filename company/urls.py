from django.urls import path

from company.views import Dashboard, UpdateCompanyProfileView

urlpatterns = [
    path('<slug:slug>/', Dashboard.as_view(), name='dashboard'),
    path('<slug:slug>/update/', UpdateCompanyProfileView.as_view(), name='update-company-profile')
]