from django import forms

from company.models import BankAccountType


class BankAccountTypeUpdateForm(forms.ModelForm):
    class Meta:
        model = BankAccountType
        fields = [
            "name",
            "description",
            "maximum_withdrawal_amount",
            "active",
            "annual_interest_rate",
            "interest_calculation_per_year"
        ]

    def __init__(self, *args, **kwargs):
        super(BankAccountTypeUpdateForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'form-control'
                )
            })

