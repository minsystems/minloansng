# Generated by Django 3.0.2 on 2021-05-09 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrowers', '0011_borrower_account_balance_on_commercial_bank_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrower',
            name='mono_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
