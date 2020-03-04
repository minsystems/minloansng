from django.db import models


# Create your models here.

class BankCode(models.Model):
    name = models.CharField(blank=True, null=True, max_length=300)
    code = models.CharField(blank=True, null=True, max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '{bank}: {code}'.format(bank=self.name, code=self.code)
