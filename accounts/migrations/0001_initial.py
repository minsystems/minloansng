# Generated by Django 3.0.2 on 2020-05-17 17:05

import accounts.models
import cloudinary.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import minloansng.utils
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailActivation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('key', models.CharField(blank=True, max_length=120, null=True)),
                ('activated', models.BooleanField(default=False)),
                ('forced_expired', models.BooleanField(default=False)),
                ('expires', models.IntegerField(default=7)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GuestEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('active', models.BooleanField(default=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name=accounts.models.upload_image_path)),
                ('keycode', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('is_premium', models.BooleanField(default=False)),
                ('trial_days', models.DateTimeField(default=minloansng.utils.get_trial_days)),
                ('token', models.CharField(blank=True, max_length=300, null=True)),
                ('role', models.CharField(blank=True, choices=[('Admin', 'Admin'), ('Staff', 'Staff'), ('Customer', 'Customer')], default='Admin', max_length=20, null=True)),
                ('plan', models.CharField(blank=True, choices=[('FREEMIUM', 'FREEMIUM'), ('STARTUP', 'STARTUP'), ('BUSINESS', 'BUSINESS'), ('ENTERPRISE', 'ENTERPRISE')], default='FREEMIUM', max_length=20, null=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
                'db_table': 'profile',
            },
        ),
    ]
