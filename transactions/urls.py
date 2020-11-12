from django.urls import path

from .views import DepositMoneyView, WithdrawMoneyView, TransactionRepostView, TransactionForMFB


app_name = 'transactions'


urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("<slug:slug>/list/", TransactionForMFB.as_view(), name="transaction_list"),
    path("<slug:slug>/report/", TransactionRepostView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
]