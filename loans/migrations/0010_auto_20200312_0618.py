# Generated by Django 3.0.2 on 2020-03-12 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0009_auto_20200311_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penalty',
            name='re_occuring',
            field=models.BooleanField(default=False),
        ),
    ]
