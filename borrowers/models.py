from cloudinary.models import CloudinaryField
from datetime import date
from django.db import models

# Create your models here.
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

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
    first_name = models.CharField(blank=True, null=True, max_length=300)
    last_name = models.CharField(blank=True, null=True, max_length=300)
    photo = CloudinaryField(upload_image_path, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True, help_text='Block 32, Arizona Street')
    lga = models.CharField(max_length=300, blank=True, null=True)
    state = models.CharField(max_length=300, choices=STATE, blank=True, null=True, help_text='Province/State')
    country = CountryField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=300)
    phone = PhoneNumberField(blank=True, null=True)
    land_line = PhoneNumberField(blank=True, null=True)
    business_name = models.CharField(max_length=300, blank=True, null=True)
    working_status = models.CharField(max_length=300, choices=WORKING_STATUS, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    unique_identifier = models.CharField(blank=True, null=True, max_length=300,
                                         help_text='Social Security Number, License Or Registration ID')
    bank = models.ForeignKey(BankCode, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    account_number = models.CharField(blank=True, null=True, max_length=100)
    bvn = models.CharField(blank=True, null=True, max_length=300, help_text='Bank Verification Number')
    date_of_birth = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        unique_together = ('slug', 'phone', 'email')

    def __str__(self):
        return "{title}, {f_name} {l_name}".format(title=self.title, f_name=self.first_name, l_name=self.last_name)

    def get_borrowers_full_name(self):
        return "{title}, {f_name} {l_name}".format(title=self.title, f_name=self.first_name, l_name=self.last_name)

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
        if self.photo:
            return self.photo.url
        return "https://img.icons8.com/officel/2x/user.png"

    def get_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return "Not Specified"


class BorrowerGroup(models.Model):
    registered_to = models.ForeignKey(to='company.Company', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=300)
    borrowers = models.ManyToManyField(Borrower, related_name='members')
    group_leader = models.ForeignKey(Borrower, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name='group_leader')
    collector = models.ForeignKey(Borrower, blank=True, null=True, on_delete=models.CASCADE)
    meeting_schedule = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=300, blank=True, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('slug', 'name')
