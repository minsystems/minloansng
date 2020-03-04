from django.db import models


# Create your models here.
from accounts.models import Profile


class Comments(models.Model):
    account_officer = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
