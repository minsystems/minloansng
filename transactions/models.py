from django.db import models

from borrowers.models import BorrowerBankAccount
from .constants import TRANSACTION_TYPE_CHOICES


class Transaction(models.Model):
    company = models.ForeignKey(to='company.Company', on_delete=models.CASCADE, blank=True, null=True)
    account = models.ForeignKey(
        BorrowerBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.account.account_no)

    class Meta:
        ordering = ['timestamp']

    def get_display_name(self):
        if self.transaction_type == 1:
            return 'Deposit'
        elif self.transaction_type == 2:
            return 'Withdrawal'
        elif self.transaction_type == 3:
            return 'Interest'
        else:
            return None
