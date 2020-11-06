from django.urls import path

from loans.views import LoanCreateView, LoanListView, LoanDetailView, RemitaStandingOrder, RemitaMandateUpdate, \
    LoanCollateralDetail, CollateralFormProcessor, LoanDetailAutoSaveProcessor, LoanCommentProcessor, \
    LoanRepaymentProcessor, LoanStatusChangeProcessor, RemitaTransRefUpdate, RRRandTransactionRef, RRRandTransactionRefAmount, \
    RemitaDDMandateTransactionRecord, RemitaDDStatusReport, LoanPenaltyRepayment

urlpatterns = [
    path('<slug:slug>/create/', LoanCreateView.as_view(), name='loan-create'),
    path('<slug:slug>/list/', LoanListView.as_view(), name='loan-list'),
    path('<slug:slug>/<slug:loan_slug>/detail/', LoanDetailView.as_view(), name='loan-detail'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/collateral/', LoanCollateralDetail.as_view(), name='loan-detail-collateral'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/', RemitaStandingOrder.as_view(), name='loan-standing-order-create'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/update/', RemitaMandateUpdate.as_view(), name='loan-mandate-update'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/update/remitaTransRef/', RemitaTransRefUpdate.as_view(), name='loan-mandate-update-remitaTransRef'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/update/rrr-update/', RRRandTransactionRef.as_view(), name='loan-mandate-update-rrr'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/update/rrr-amount-update/', RRRandTransactionRefAmount.as_view(), name='loan-mandate-update-rrr-amount'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/mandate-dd-record/', RemitaDDMandateTransactionRecord.as_view(), name='mandate-dd-record'),
    path('<slug:slug>/<slug:loan_slug>/<slug:loan_key>/mandate-dd-status-report/', RemitaDDStatusReport.as_view(), name='mandate-dd-status-report'),

    path('collateral-processor/', CollateralFormProcessor.as_view(), name='collateral-processor'),
    path('description-processor/', LoanDetailAutoSaveProcessor.as_view(), name='description-processor'),
    path('loan-comment-processor/', LoanCommentProcessor.as_view(), name='comment-processor'),
    path('update-repayment-processor/', LoanRepaymentProcessor.as_view(), name='repayment-processor'),
    path('loan-status-change-processor/', LoanStatusChangeProcessor.as_view(), name='loan-status-change-processor'),
    path('loan-penalty-processor/', LoanPenaltyRepayment.as_view(), name='loan-penalty-processor'),
]
