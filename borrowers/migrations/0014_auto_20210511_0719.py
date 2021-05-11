# Generated by Django 3.0.2 on 2021-05-11 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrowers', '0013_auto_20210511_0643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrower',
            name='account_balance_on_commercial_bank_account',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='account_number',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='address',
            field=models.CharField(blank=True, help_text='Block 32, Arizona Street', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='business_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='bvn',
            field=models.CharField(blank=True, help_text='Bank Verification Number', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='first_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')], max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='last_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='lga',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='mono_code',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='slug',
            field=models.SlugField(blank=True, max_length=500, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='state',
            field=models.CharField(blank=True, choices=[('Lagos', 'Lagos'), ('Kano', 'Kano'), ('Enugu', 'Enugu')], help_text='Province/State', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='title',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='unique_identifier',
            field=models.CharField(blank=True, help_text='Social Security Number, License Or Registration ID', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='working_status',
            field=models.CharField(blank=True, choices=[('Employed', 'Employed'), ('Unemployed', 'Unemployed'), ('Self-Employed', 'Self-Employed')], max_length=500, null=True),
        ),
    ]
