# Generated by Django 3.0.2 on 2020-10-13 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_thirdpartycreds'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='thirdpartycreds',
            options={'verbose_name': 'Third Party Credentials', 'verbose_name_plural': 'Third Party Credentials'},
        ),
    ]
