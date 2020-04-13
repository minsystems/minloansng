from django.urls import path

from loans.views import LoanCreateView, LoanListView, LoanDetailView

urlpatterns = [
    path('<slug:slug>/create/', LoanCreateView.as_view(), name='loan-create'),
    path('<slug:slug>/list/', LoanListView.as_view(), name='loan-list'),
    path('<slug:slug>/<slug:loan_slug>/detail/', LoanDetailView.as_view(), name='loan-detail'),
]
