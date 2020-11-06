from django.db import models


# Create your models here.


class MinOneDescription(models.Model):
    maintenance_mode = models.BooleanField(default=False)
    description = models.TextField()
    price = models.PositiveIntegerField(default=3400)
    key = models.CharField(max_length=10, blank=True, null=True, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(blank=True, to='accounts.Profile')

    who_uses_minone = models.TextField()
    benefit_of_minone_to_lenders = models.TextField()
    benefit_of_minone_to_borrowers = models.TextField()

    class Meta:
        db_table = "minone_description"
        verbose_name = "Minone Description"
        verbose_name_plural = "Minone Description"
        unique_together = ('key',)

    def __str__(self):
        return self.key
