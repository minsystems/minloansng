from cloudinary.forms import CloudinaryFileField
from django import forms
from django.conf import settings
from django.db import transaction

from accounts.constants import GENDER_CHOICE
from borrowers.models import Borrower, BorrowerBankAccount
from company.models import BankAccountType


class BorrowerUpdateForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = (
            'title',
            'photo',
            'first_name',
            'last_name',
            'gender',
            'address',
            'lga',
            'state',
            'country',
            'phone',
            'land_line',
            'business_name',
            'working_status',
            'email',
            'unique_identifier',
            'bank',
            'account_number',
            'bvn',
            'date_of_birth',
        )


class BorrowerBankAccountForm(forms.ModelForm):

    class Meta:
        model = BorrowerBankAccount
        fields = (
            'account_type',
            'account_no',
            'balance',
            'interest_start_date',
            'initial_deposit_date',
            'active'
        )

    def __init__(self, company, *args, **kwargs):
        super(BorrowerBankAccountForm, self).__init__(company, *args, **kwargs)
        print(kwargs)
        # self.fields['account_type'].queryset = BankAccountType.objects.filter(company=company)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control'
                )
            })

    @transaction.atomic
    def save(self, commit=True):
        bank_account = super(BorrowerBankAccountForm, self).save(commit=False)
        if commit:
            bank_account.save()
            print(self.cleaned_data)

            # BorrowerBankAccount.objects.create(
            #     borrower=borrower,
            #     company=
            #     gender=gender,
            #     birth_date=birth_date,
            #     account_type=account_type,
            #     account_no=(
            #             user.id +
            #             settings.ACCOUNT_NUMBER_START_FROM
            #     )
            # )
        return bank_account
