from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView

from borrowers.models import Borrower, BorrowerBankAccount
from company.models import Company
from transactions.constants import DEPOSIT, WITHDRAWAL
from transactions.forms import (
    DepositForm,
    TransactionDateRangeForm,
    WithdrawForm,
)
from transactions.models import Transaction


class TransactionForMFB(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_list.html'
    model = Transaction

    def get_queryset(self):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        qs = self.model.objects.filter(company=company)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TransactionForMFB, self).get_context_data(**kwargs)
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        userCompany_qs = company.user.user.profile.company_set.all()
        context['company'] = company
        context.update({
            'object': company,
            'company': company,
            'bank_transactions': self.get_queryset(),
            'userCompany_qs': userCompany_qs,
        })
        return context


class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data
        return super().get(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        print(**kwargs)
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None)
        })

        return context


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(LoginRequiredMixin, DetailView):
    template_name = 'transactions/transaction-deposit.html'
    model = Company
    title = 'Deposit Money To Account'

    def get_context_data(self, **kwargs):
        context = super(DepositMoneyView, self).get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'company': self.get_object(),
            'userCompany_qs': self.get_object().user.company_set.all(),
            'borrowers_qs': self.get_object().borrower_set.all()
        })
        return context

    def post(self, *args, **kwargs):
        print(self.request.POST)
        if self.request.POST.get('transactionType') == 'Deposit':
            amount = int(self.request.POST.get('amount'))
            borrower = Borrower.objects.get(slug__iexact=self.request.POST.get('borrower'))
            borrower_account = BorrowerBankAccount.objects.get(borrower=borrower)
            if not borrower_account.initial_deposit_date:
                print("here worked!")
                now = timezone.now()
                next_interest_month = int(12 / borrower_account.account_type.interest_calculation_per_year)
                borrower_account.initial_deposit_date = now
                borrower_account.interest_start_date = (
                    now + relativedelta(months=+next_interest_month)
                )
                borrower_account.company = self.get_object()
                borrower_account.borrower = borrower
                borrower_account.balance += amount
                borrower_account.save(
                    update_fields=[
                        'company',
                        'borrower',
                        'initial_deposit_date',
                        'balance',
                        'interest_start_date'
                    ]
                )
                borrower_account_new = BorrowerBankAccount.objects.get(borrower=borrower)
                Transaction.objects.create(
                    company=self.get_object(),
                    account=borrower_account,
                    amount=amount,
                    balance_after_transaction=borrower_account_new.balance,
                    transaction_type=1
                )
                payload_message = f'₦{amount} was deposited to your account successfully'
                return JsonResponse({'message': payload_message})
            else:
                borrower_account.company = self.get_object()
                borrower_account.borrower = borrower
                borrower_account.balance += amount
                borrower_account.save(
                    update_fields=[
                        'company',
                        'borrower',
                        'balance',
                    ]
                )
                borrower_account_new = BorrowerBankAccount.objects.get(borrower=borrower)
                Transaction.objects.create(
                    company=self.get_object(),
                    account=borrower_account,
                    amount=amount,
                    balance_after_transaction=borrower_account_new.balance,
                    transaction_type=1
                )
                payload_message = f'₦{amount} was deposited to your account successfully'
                return JsonResponse({'message': payload_message})
        else:
            amount = int(self.request.POST.get('amount'))
            borrower = Borrower.objects.get(slug__iexact=self.request.POST.get('borrower'))
            borrower_account = BorrowerBankAccount.objects.get(borrower=borrower)

            if borrower_account.balance >= amount:
                borrower_account.balance -= amount

                borrower_account.save(update_fields=['balance'])

                borrower_account_new = BorrowerBankAccount.objects.get(borrower=borrower)
                Transaction.objects.create(
                    company=self.get_object(),
                    account=borrower_account,
                    amount=amount,
                    balance_after_transaction=borrower_account_new.balance,
                    transaction_type=2
                )

                payload_message = f'Successfully withdrawn ₦{amount} from your account'
                return JsonResponse({'message': payload_message})
            else:
                payload_message = f'Request amount ₦{amount} cannot be withdrawn from your balance ₦{borrower_account.balance}'
                return JsonResponse({'message': payload_message})


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money from Your Account'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn ₦{amount} from your account'
        )

        return super().form_valid(form)
