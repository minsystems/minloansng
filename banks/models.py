from django.db import models


# Create your models here.

class BankCode(models.Model):
    name = models.CharField(blank=True, null=True, max_length=300)
    code = models.CharField(blank=True, null=True, max_length=300)
    otp_enabled = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    @property
    def getBankCodeAndName(self):
        return '{bank}: {code}'.format(bank=self.name, code=self.code)

    def get_short_name(self):
        line = self.name
        chars = ""
        words = line.split()
        for word in words:
            chars = chars + word[0]
        return ".".join(chars).upper()