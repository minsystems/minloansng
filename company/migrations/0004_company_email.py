# Generated by Django 3.0.2 on 2020-02-13 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_auto_20200209_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
    ]
