from cloudinary.models import CloudinaryField
from datetime import date
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from accounts.constants import GENDER_CHOICE
from accounts.models import upload_image_path
from banks.models import BankCode

GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

STATE = (
    ('Lagos', 'Lagos'),
    ('Kano', 'Kano'),
    ('Enugu', 'Enugu')
)

WORKING_STATUS = (
    ('Employed', 'Employed'),
    ('Unemployed', 'Unemployed'),
    ('Self-Employed', 'Self-Employed'),
)


class Borrower(models.Model):
    registered_to = models.ForeignKey(to='company.Company', on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(blank=True, null=True, max_length=255)
    last_name = models.CharField(blank=True, null=True, max_length=255)
    photo = CloudinaryField(upload_image_path, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True, help_text='Block 32, Arizona Street')
    lga = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, choices=STATE, blank=True, null=True, help_text='Province/State')
    country = CountryField(blank=True, null=True, max_length=255)
    title = models.CharField(blank=True, null=True, max_length=255)
    phone = PhoneNumberField(blank=True, null=True)
    land_line = PhoneNumberField(blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    working_status = models.CharField(max_length=255, choices=WORKING_STATUS, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    unique_identifier = models.CharField(blank=True, null=True, max_length=255,
                                         help_text='Social Security Number, License Or Registration ID')
    bank = models.ForeignKey(BankCode, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    account_number = models.CharField(blank=True, null=True, max_length=255)
    bvn = models.CharField(blank=True, null=True, max_length=255, help_text='Bank Verification Number')
    date_of_birth = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return "{title}, {f_name} {l_name}".format(title=self.title, f_name=self.first_name, l_name=self.last_name)

    def get_borrowers_full_name(self):
        return "{title}, {f_name} {l_name}".format(title=self.title, f_name=self.first_name, l_name=self.last_name)

    def get_short_name(self):
        return "{f_name}".format(f_name=self.first_name)

    def get_address(self):
        return "{address}, {lga} {state} {country}".format(address=self.address, lga=self.lga, state=self.state,
                                                           country=self.country)

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="100" height="100" />' % self.photo.url)

    image_tag.short_description = 'Profile Image'
    image_tag.allow_tags = True

    @property
    def get_image(self):
        if self.photo or self.photo == "":
            return self.photo.url
        return "https://img.icons8.com/officel/2x/user.png"

    def get_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                        (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return "Not Specified"

    def get_absolute_url(self):
        return reverse("borrowers-url:borrower-detail", kwargs={"slug":self.registered_to.slug, "slug_borrower": self.slug})

    @property
    def balance(self):
        if hasattr(self, 'account'):
            return self.account.balance
        return 0


class BorrowerBankAccount(models.Model):
    company = models.ForeignKey(to='company.Company', on_delete=models.CASCADE, blank=True, null=True)
    borrower = models.OneToOneField(
        Borrower,
        related_name='account',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    account_type = models.ForeignKey(
        to='company.BankAccountType',
        related_name='accounts',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    account_no = models.PositiveIntegerField(unique=True)
    balance = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )
    interest_start_date = models.DateField(
        null=True, blank=True,
        help_text=(
            'The month number that interest calculation will start from'
        )
    )
    initial_deposit_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.account_no)

    def get_interest_calculation_months(self):
        """
        List of month numbers for which the interest will be calculated
        returns [2, 4, 6, 8, 10, 12] for every 2 months interval
        """
        interval = int(
            12 / self.account_type.interest_calculation_per_year
        )
        start = self.interest_start_date.month
        return [i for i in range(start, 13, interval)]


class BorrowerGroup(models.Model):
    registered_to = models.ForeignKey(to='company.Company', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=300)
    borrowers = models.ManyToManyField(Borrower, related_name='members')
    group_leader = models.ForeignKey(Borrower, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name='group_leader')
    collector = models.ForeignKey(Borrower, blank=True, null=True, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=300, blank=True, null=True)
    description = models.TextField()
    color_code = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('slug', 'name')
