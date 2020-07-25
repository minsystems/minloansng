# Generated by Django 3.0.2 on 2020-06-17 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('borrowers', '0001_initial'),
        ('banks', '0001_initial'),
        ('company', '0002_remitacredentials'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemitaMandateActivationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(blank=True, max_length=100, null=True)),
                ('hash_key', models.CharField(blank=True, max_length=200, null=True)),
                ('max_number_of_debits', models.CharField(blank=True, max_length=100, null=True)),
                ('requestId', models.CharField(blank=True, max_length=200, null=True)),
                ('serviceTypeId', models.CharField(blank=True, max_length=200, null=True)),
                ('start_date', models.CharField(blank=True, max_length=200, null=True)),
                ('end_date', models.CharField(blank=True, max_length=200, null=True)),
                ('connected_firm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
                ('mandate_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mandateTypeData', to='company.RemitaCredentials')),
                ('merchantId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='merchantIdData', to='company.RemitaCredentials')),
                ('payer_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payerAccount', to='borrowers.Borrower')),
                ('payer_bank_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='banks.BankCode')),
                ('payer_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payerEmail', to='borrowers.Borrower')),
                ('payer_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payerName', to='borrowers.Borrower')),
                ('payer_phone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payerPhone', to='borrowers.Borrower')),
            ],
        ),
    ]