# Generated by Django 3.0.2 on 2020-12-06 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minmarkets', '0005_delete_featuredpackages'),
    ]

    operations = [
        migrations.AddField(
            model_name='identityverificationpackage',
            name='featured',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='loancalculators',
            name='featured',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='loancollectionpackage',
            name='featured',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='loanpackage',
            name='featured',
            field=models.BooleanField(default=True),
        ),
    ]
