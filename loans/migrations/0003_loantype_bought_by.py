# Generated by Django 3.0.2 on 2020-02-27 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20200222_1029'),
        ('loans', '0002_auto_20200226_0700'),
    ]

    operations = [
        migrations.AddField(
            model_name='loantype',
            name='bought_by',
            field=models.ManyToManyField(to='accounts.Profile'),
        ),
    ]
