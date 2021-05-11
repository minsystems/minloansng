# Generated by Django 3.0.2 on 2021-05-11 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrowers', '0012_borrower_mono_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrower',
            name='address',
            field=models.CharField(blank=True, help_text='Block 32, Arizona Street', max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')], max_length=255, null=True),
        ),
    ]