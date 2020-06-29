from django.urls import path

from loans.views import LoanCreateView, LoanListView, LoanDetailView, RemitaStandingOrder, RemitaMandateUpdate

urlpatterns = [
    path('<slug:slug>/create/', LoanCreateView.as_view(), name='loan-create'),
    path('<slug:slug>/list/', LoanListView.as_view(), name='loan-list'),
    path('<slug:slug>/<slug:loan_slug>/detail/', LoanDetailView.as_view(), name='loan-detail'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/', RemitaStandingOrder.as_view(), name='loan-standing-order-create'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/update/', RemitaMandateUpdate.as_view(), name='loan-mandate-update'),
]
