# Generated by Django 3.0.2 on 2020-02-09 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20200209_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
    ]
