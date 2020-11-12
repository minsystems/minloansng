from django.urls import path

from borrowers.views import (
    BorrowerCreateView, BorrowerGroupCreateView, BorrowerUpdateView, BorrowerGroupsListView,
    BorrowerListView,BorrowerDetailView, AssignBankAccountToBorrower, CustomerAccountList
)

urlpatterns = [
    path('<slug:slug>/create/', BorrowerCreateView.as_view(), name='borrower-create'),
    path('<slug:slug>/list/', BorrowerListView.as_view(), name='borrower-list'),
    path('<slug:slug>/<slug:slug_borrower>/detail-update/', BorrowerUpdateView.as_view(), name='borrower-update'),
    path('<slug:slug>/<slug:slug_borrower>/detail/', BorrowerDetailView.as_view(), name='borrower-detail'),

    path('<slug:slug>/assign-account/', AssignBankAccountToBorrower.as_view(), name='borrower-account-create'),
    path('<slug:slug>/customer-savings-account/list/', CustomerAccountList.as_view(), name='borrower-account-list'),

    path('<slug:slug>/group/create/', BorrowerGroupCreateView.as_view(), name='borrower-group-create'),
    path('<slug:slug>/group/list/', BorrowerGroupsListView.as_view(), name='borrower-group-list'),
]
