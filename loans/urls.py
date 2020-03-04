from django.urls import path

from loans.views import LoanCreateView

urlpatterns = [
    path('<slug:slug>/create/', LoanCreateView.as_view(), name='loan-create'),
    # path('<slug:slug>/<slug:loan_slug>/create/', LoanCreateView.as_view(), name='loan-create'),
]
