# Generated by Django 3.0.2 on 2020-02-09 18:46

from django.db import migrations, models
import minloansng.utils


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200206_0739'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='trial_days',
            field=models.DateTimeField(default=minloansng.utils.get_trial_days),
        ),
    ]
