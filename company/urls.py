from django.urls import path

from company.views import (
    Dashboard, UpdateCompanyProfileView, CompanyAccountTypesList,
    CompanyAccountTypeDetails, CompanyAccountTypeUpdate, CompanyAccountTypeDelete, CompanyAccountCreateForm
)

urlpatterns = [
    path('<slug:slug>/', Dashboard.as_view(), name='dashboard'),
    path('<slug:slug>/update/', UpdateCompanyProfileView.as_view(), name='update-company-profile'),
    path('<slug:company_slug>/account-type-create/', CompanyAccountCreateForm.as_view(), name='bank-account-type-create'),
    path('<slug:slug>/account-type/', CompanyAccountTypesList.as_view(), name='bank-account-type'),
    path('<slug:company_slug>/<slug:slug>/account-type-details/', CompanyAccountTypeDetails.as_view(), name='bank-account-type-details'),
    path('<slug:company_slug>/<slug:slug>/account-type-update/', CompanyAccountTypeUpdate.as_view(), name='bank-account-type-update'),
    path('<slug:company_slug>/<slug:slug>/account-type-delete/', CompanyAccountTypeDelete.as_view(), name='bank-account-type-delete'),
]