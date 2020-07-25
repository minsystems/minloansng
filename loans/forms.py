from django import forms

from loans.models import Collateral, Loan


class CollateralForm(forms.ModelForm):
    class Meta:
        model = Collateral
        fields = [
            'collateral_type', 'name', 'registered_date', 'status', 'value', 'condition',
            'collateral_files'
        ]
        widgets = {'collateral_files': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(CollateralForm, self).__init__(*args, **kwargs)
        # self.fields['collateral_files'].widget = self.HiddenInput()
        # # for field in self.fields:
        # #     field.required = True


class LoanFileForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
            'loan_file_upload'
        ]

    def clean_loan_file_upload(self):
        file = self.cleaned_data['loan_file_upload']
        if file is None:
            raise forms.ValidationError('file content cannot be empty')
        return file
