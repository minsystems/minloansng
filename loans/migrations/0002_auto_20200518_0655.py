# Generated by Django 3.0.2 on 2020-05-18 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('minmarkets', '0002_auto_20200517_1124'),
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modeofrepayments',
            name='package',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='minmarkets.LoanCollectionPackage'),
        ),
    ]
