from cloudinary.models import CloudinaryField
from django.db import models

# Create your models here.
from accounts.models import Profile, upload_image_path


class LoanPackage(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)
    price = models.IntegerField(default=3000)
    premium_package = models.BooleanField(default=True)
    package_owner = models.CharField(max_length=300)
    description = models.TextField()
    product_code = models.CharField(null=True, blank=True, max_length=10)
    image = CloudinaryField(upload_image_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="150" height="200" />' % self.image.url)

    image_tag.short_description = 'Package Image'
    image_tag.allow_tags = True


class LoanCalculators(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)
    price = models.IntegerField(default=3000)
    premium_package = models.BooleanField(default=True)
    package_owner = models.CharField(max_length=300)
    description = models.TextField()
    file = models.CharField(max_length=300, blank=True, null=True, help_text="download link here!")
    product_code = models.CharField(null=True, blank=True, max_length=10)
    image = CloudinaryField(upload_image_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Loan Calculator'
        verbose_name_plural = 'Loan Calculators'

    def __str__(self):
        return self.name

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="100" height="100" />' % self.image.url)

    image_tag.short_description = 'Package Image'
    image_tag.allow_tags = True


class LoanCollectionPackage(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)
    price = models.IntegerField(default=3000)
    premium_package = models.BooleanField(default=True)
    package_owner = models.CharField(max_length=300)
    description = models.TextField()
    product_code = models.CharField(null=True, blank=True, max_length=10)
    image = CloudinaryField(upload_image_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="150" height="200" />' % self.image.url)

    image_tag.short_description = 'Package Image'
    image_tag.allow_tags = True
