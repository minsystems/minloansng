from cloudinary.forms import CloudinaryFileField
from django import forms

from borrowers.models import Borrower


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
