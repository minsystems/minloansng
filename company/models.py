from cloudinary.models import CloudinaryField
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.urls import reverse

from accounts.models import Profile, upload_image_path
from minloansng.utils import unique_slug_generator


class Branch(models.Model):
    branch_custom = models.CharField(max_length=300, blank=True, null=True,
                                     help_text="Assign a unique ID to this branch")
    slug = models.SlugField(blank=True, null=True, unique=True)
    address = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "branch"
        verbose_name = "branch"
        verbose_name_plural = "branches"

    def __str__(self):
        return self.branch_custom


class CompanyQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class CompanyManager(models.Manager):
    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def get_by_id(self):
        qs = self.get_queryset().filter(id=id)
        if qs.count == 1:
            return qs.first()
        return None


class Company(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, null=True, default='')
    email = models.CharField(max_length=300, blank=True, null=True, default='')
    staffs = models.ManyToManyField(to='accounts.Profile', related_name='workers')
    logo = CloudinaryField(upload_image_path, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CompanyManager()

    # reverse relationship
    # company_set = Bus.trips_set.all().count()

    class Meta:
        db_table = "company"
        verbose_name = "company"
        verbose_name_plural = "companies"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_logo(self):
        if self.logo:
            return self.logo.url
        return 'https://clipartart.com/images/company-building-clipart-png-22.jpg'

    def get_absolute_url(self):
        return reverse("company-url:dashboard", kwargs={"slug": self.slug})

    def get_email(self):
        if self.email is not None:
            return self.email
        return self.user.user.email


def post_save_user_create_reciever(sender, instance, created, *args, **kwargs):
    if created:
        Company.objects.create(user=instance, slug=unique_slug_generator(instance))


post_save.connect(post_save_user_create_reciever, sender=Profile)


class RemitaCredentials(models.Model):
    connected_firm = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    merchantId = models.CharField(max_length=200, blank=True, null=True)
    serviceTypeId = models.CharField(max_length=200, blank=True, null=True)
    apiKey = models.CharField(max_length=200, blank=True, null=True)
    mandateType = models.CharField(max_length=100, default="DD")

    class Meta:
        verbose_name = "Remita Credentials"
        verbose_name_plural = "Remita Credentials"

    def __str__(self):
        return self.connected_firm.name


class RemitaMandateActivationData(models.Model):
    connected_firm = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    loan_key = models.OneToOneField(to="loans.Loan", on_delete=models.CASCADE, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    amount_debited_at_instance = models.CharField(max_length=100, blank=True, null=True)
    hash_key = models.CharField(max_length=200, blank=True, null=True)
    mandate_type = models.CharField(max_length=200, blank=True, null=True)
    max_number_of_debits = models.CharField(max_length=100, blank=True, null=True)
    merchantId = models.CharField(max_length=200, blank=True, null=True)
    payer_name = models.CharField(max_length=200, blank=True, null=True)
    payer_phone = models.CharField(max_length=200, blank=True, null=True)
    payer_account = models.CharField(max_length=200, blank=True, null=True)
    payer_bank_code = models.CharField(max_length=200, blank=True, null=True)
    payer_email = models.CharField(max_length=200, blank=True, null=True)
    requestId = models.CharField(max_length=200, blank=True, null=True)
    serviceTypeId = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.CharField(max_length=200, blank=True, null=True)
    end_date = models.CharField(max_length=200, blank=True, null=True)
    remitaTransRef = models.CharField(max_length=200, blank=True, null=True)
    statuscode = models.CharField(max_length=200, blank=True, null=True)
    rrr = models.CharField(max_length=200, blank=True, null=True)
    transactionRef = models.CharField(max_length=200, blank=True, null=True)
    mandateId = models.CharField(max_length=200, blank=True, null=True)
    mandate_requestId = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, null=True)
    lastStatusUpdateTime = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.requestId


class RemitaMandateTransactionRecord(models.Model):
    remita_dd_mandate_owned_record = models.ForeignKey(RemitaMandateActivationData, on_delete=models.CASCADE,
                                                       blank=True, null=True)
    loan = models.ForeignKey(to='loans.Loan', on_delete=models.CASCADE, blank=True, null=True)
    total_transaction_count = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Remita Mandate Transaction Record"
        verbose_name_plural = "Remita Mandate Transaction Record"

    def __str__(self):
        return str(self.remita_dd_mandate_owned_record.mandate_requestId)


class RemitaPaymentDetails(models.Model):
    loan = models.ForeignKey(to='loans.Loan', on_delete=models.CASCADE, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    lastStatusUpdateTime = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    statuscode = models.CharField(max_length=100, blank=True, null=True)
    RRR = models.CharField(max_length=100, blank=True, null=True)
    transactionRef = models.CharField(max_length=100, blank=True, null=True)
    remita_transactions = models.ForeignKey(RemitaMandateTransactionRecord, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Remita Payment Details"
        verbose_name_plural = "Remita Payment Details"

    def __str__(self):
        return self.lastStatusUpdateTime


class RemitaMandateStatusReport(models.Model):
    loan = models.ForeignKey(to='loans.Loan', on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.CharField(max_length=100, blank=True, null=True)
    end_date = models.CharField(max_length=100, blank=True, null=True)
    request_id = models.CharField(max_length=100, blank=True, null=True)
    mandate_id = models.CharField(max_length=100, blank=True, null=True)
    registration_date = models.CharField(max_length=100, blank=True, null=True, help_text="Mandate Registered On: ")
    mandate_status = models.BooleanField(default=True)
    report_status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Remita Mandate Status Report"
        verbose_name_plural = "Remita Mandate Status Reports"

    def __str__(self):
        return self.mandate_id