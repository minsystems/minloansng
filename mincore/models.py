from cloudinary.models import CloudinaryField
from django.db import models

# Create your models here.
from django.urls import reverse

from accounts.models import upload_image_path, Profile
from company.models import Company


class SubscribersManager(models.Manager):
    def active(self):
        return super(SubscribersManager, self).filter(active=True)


class Subscribers(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = SubscribersManager()

    class Meta:
        verbose_name = 'Subscribers'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email


class MessagesManager(models.Manager):
    def all(self):
        return super(MessagesManager, self).filter(active=True)


class Messages(models.Model):
    to_obj = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    to_all = models.BooleanField(default=False)
    from_obj = models.CharField(max_length=300, default='Mincore Systems')
    title = models.CharField(max_length=200, blank=True, null=True)
    image = CloudinaryField(upload_image_path, null=True, blank=True)
    content = models.TextField()
    url = models.URLField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = MessagesManager()

    class Meta:
        verbose_name = 'messages'
        verbose_name_plural = 'messages'

    def __str__(self):
        return self.title

    def get_image(self):
        if self.image:
            return self.image.url
        return 'https://cdn.minloans.com.ng/images/minloansng2.png'

    def get_absolute_url(self, company_inst):
        return reverse('mincore-url:message-detail', kwargs={'slug': company_inst, 'slug_message': self.slug})


class SupportTickets(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=300)
    content = models.TextField()
    ticket_id = models.CharField(max_length=300, blank=True, null=True)
    affected_company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Ticket'
        ordering = ("-timestamp", "-updated",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('mincore-url:support-ticket', kwargs={'slug': self.slug})


class PlanDetails(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    max_staff = models.PositiveIntegerField(blank=True, null=True)
    maintenance_fee = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Pricing Plan'
        verbose_name_plural = 'Pricing Plans'

    def __str__(self):
        return self.name


class BaseUrl(models.Model):
    belongs_to = models.CharField(max_length=300, blank=True, null=True)
    base_url = models.CharField(max_length=300, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Base URL'
        verbose_name_plural = 'Base URLs'

    def __str__(self):
        return self.base_url

