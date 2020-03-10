from django.urls import path

from borrowers.views import BorrowerCreateView, BorrowerGroupCreateView, BorrowerUpdateView

urlpatterns = [
    path('<slug:slug>/create/', BorrowerCreateView.as_view(), name='borrower-create'),
    path('<slug:slug>/<slug:slug_borrower>/update/', BorrowerUpdateView.as_view(), name='borrower-update'),
    path('<slug:slug>/group/create/', BorrowerGroupCreateView.as_view(), name='borrower-group-create'),
]
