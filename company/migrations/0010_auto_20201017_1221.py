# Generated by Django 3.0.2 on 2020-10-17 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_auto_20201017_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remitamandateactivationdata',
            name='connected_firm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.Company'),
        ),
    ]
