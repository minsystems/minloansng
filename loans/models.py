from cloudinary.models import CloudinaryField
from dateutil.relativedelta import relativedelta
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime

from accounts.models import Profile, upload_image_path
from borrowers.models import Borrower
from company.models import Company
from minloansng.utils import unique_slug_by_name, digitExtract, secondWordExtract
from minmarkets.models import LoanPackage, LoanCollectionPackage

INTEREST_PLAN = (
    ('Per Year', 'Per Year'),
    ('Per Month', 'Per Month'),
    ('Per Week', 'Per Week'),
    ('Per Day', 'Per Day')
)

DURATION_PLAN = (
    ('Years', 'Years'),
    ('Months', 'Months'),
    ('Weeks', 'Weeks'),
    ('Days', 'Days')
)

REPAYMENT_PLAN = (
    ('Yearly', 'Yearly'),
    ('Monthly', 'Monthly'),
    ('Weekly', 'Weekly'),
    ('Daily', 'Daily')
)

LOAN_STATUS = (
    ('OPEN', 'OPEN'),
    ('PARTIAL', 'PARTIAL'),
    ('CLOSED', 'CLOSED'),
    ('COMPLETED', 'COMPLETED'),
    ('OVERDUE/EXPIRED', 'OVERDUE/EXPIRED')
)

COLLATERAL_STATUS = (
    ('Deposited In Branch', 'Deposited In Branch'),
    ('Collateral With Borrower', 'Collateral With Borrower'),
    ('Returned To Borrower', 'Returned To Borrower'),
    ('Sold', 'Sold'),
    ('Lost', 'Lost')
)


class LoanTerms(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=300)
    content = models.TextField(blank=True, null=True)
    package = models.ForeignKey(LoanPackage, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Loan Terms'
        verbose_name_plural = 'Loan Terms'

    def __str__(self):
        return self.title


class ModeOfRepayments(models.Model):
    package = models.OneToOneField(LoanCollectionPackage, on_delete=models.CASCADE, blank=True, null=True)
    bought_by = models.ManyToManyField(Profile,)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Mode Of Repayment'
        verbose_name_plural = 'Mode Of Repayments'

    def __str__(self):
        return self.package.name

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="150" height="200" />' % self.package.image.url)

    image_tag.short_description = 'Package Image'
    image_tag.allow_tags = True


class Penalty(models.Model):
    title = models.CharField(max_length=300, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    describe = models.TextField()
    punishment_fee = models.CharField(max_length=300, blank=True, null=True)
    re_occuring = models.BooleanField(default=False)
    value_on_period = models.IntegerField(default=7, blank=True, null=True)
    period = models.CharField(max_length=20, choices=INTEREST_PLAN, default="Per Month", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name = 'Penalty'
        verbose_name_plural = 'Penalties'

    def __str__(self):
        return self.title


class CollateralFiles(models.Model):
    file = CloudinaryField(upload_image_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name = 'Collateral File'
        verbose_name_plural = 'Collateral Files'

    def __str__(self):
        return self.file.url


class CollateralType(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Collateral Type'
        verbose_name_plural = 'Collateral Type'

    def __str__(self):
        return self.name


class LoanType(models.Model):
    package = models.OneToOneField(LoanPackage, on_delete=models.CASCADE)
    bought_by = models.ManyToManyField(Profile)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Loan Type'
        verbose_name_plural = 'Loan Type'

    def __str__(self):
        return self.package.name

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="100" height="100" />' % self.package.image.url)

    image_tag.short_description = 'Package Image'
    image_tag.allow_tags = True


class Collateral(models.Model):
    collateral_type = models.OneToOneField(CollateralType, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=300)
    registered_date = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    status = models.CharField(max_length=40, choices=COLLATERAL_STATUS, default="OPEN", blank=True, null=True)
    value = models.CharField(max_length=300, blank=True, null=True, help_text='Object Worth')
    condition = models.TextField(help_text='Describe status of object', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField(upload_image_path, null=True, blank=True)
    collateral_files = models.ForeignKey(CollateralFiles, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Collateral'
        verbose_name_plural = 'Collateral'

    def __str__(self):
        return self.slug


class LoanQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class LoanManager(models.Manager):
    def get_queryset(self):
        return LoanQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def opened_loans(self):
        return self.all().filter(loan_status__iexact='OPEN')


class Loan(models.Model):
    account_officer = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, blank=True, null=True)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE, blank=True, null=True)
    loan_key = models.CharField(blank=True, null=True, max_length=300)
    principal_amount = models.CharField(blank=True, null=True, max_length=300)
    balance_due = models.CharField(blank=True, null=True, max_length=300)
    interest = models.PositiveIntegerField(blank=True, null=True)
    interest_period = models.CharField(max_length=20, choices=INTEREST_PLAN, default="Per Month", blank=True, null=True)
    loan_duration_circle = models.CharField(max_length=20, choices=DURATION_PLAN, default="Months", blank=True,
                                            null=True)
    loan_duration_circle_figure = models.IntegerField(default=1)
    repayment_circle = models.CharField(max_length=20, choices=REPAYMENT_PLAN, default="Monthly", blank=True,
                                        null=True)
    number_repayments = models.CharField(blank=True, null=True, max_length=300)
    release_date = models.DateTimeField(help_text='Loan Paid To Customer On:')
    collection_date = models.DateTimeField(help_text='Each Date Loan Balance Is Been Paid Back', blank=True, null=True)
    end_date = models.DateTimeField(help_text='Maturity Date', blank=True, null=True)
    processing_fee = models.CharField(blank=True, null=True, max_length=300)
    grace_period = models.IntegerField(default=1, help_text='Counts In Days')
    insurance = models.CharField(blank=True, null=True, max_length=300)
    collateral = models.OneToOneField(Collateral, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    loan_file_upload = CloudinaryField(upload_image_path, null=True, blank=True)
    active = models.BooleanField(default=True)
    loan_status = models.CharField(max_length=20, choices=LOAN_STATUS, default="OPEN", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    mode_of_repayments = models.ForeignKey(ModeOfRepayments, on_delete=models.CASCADE, blank=True, null=True)
    penalty = models.ForeignKey(Penalty, on_delete=models.CASCADE, blank=True, null=True)
    loan_terms = models.OneToOneField(LoanTerms, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = LoanManager()

    class Meta:
        db_table = "loan"
        verbose_name = "loan"
        verbose_name_plural = "loans"
        ordering = ("-timestamp",)

    def get_absolute_url(self, company_inst):
        return reverse('loans-url:loan-detail', kwargs={'slug': company_inst.slug, 'loan_slug': self.slug})

    def __str__(self):
        return self.loan_key

    def get_opened_loans_by_company(self):
        return self.objects.opened_loans().filter(company=self.company)

    # model methods
    def get_installments(self):
        return digitExtract(self.number_repayments)

    def get_interest_rate(self):
        return "{rate}% {period}".format(rate=self.interest, period=self.interest_period)

    # def get_loan_status(self):
    #     if self.get_end_date() < datetime.now():
    #         return "EXPIRED/OVERDUE"
    #     return self.loan_status
    #
    # # override the save method! each time a save method is called!
    # def save(self, *args, **kwargs):
    #     if self.get_end_date() < datetime.now():
    #         self.loan_status = "EXPIRED/OVERDUE"
    #     super(Loan, self).save(*args, **kwargs)


def post_save_user_create_reciever(sender, instance, created, *args, **kwargs):
    print(kwargs)
    print(instance.borrower)
    if created:
        Collateral.objects.get_or_create(slug=instance.loan_key)
        Penalty.objects.create(title=instance.loan_key)
        LoanTerms.objects.create(title=instance.loan_key)


post_save.connect(post_save_user_create_reciever, sender=Loan)
