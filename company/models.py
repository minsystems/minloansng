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
