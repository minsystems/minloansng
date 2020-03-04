import random
import os

from datetime import timedelta

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from sendgrid import Mail, SendGridAPIClient

from minloansng.utils import unique_key_generator, get_trial_days, unique_slug_by_name, unique_slug_generator, \
    random_string_generator
from minloansng import email_settings

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)


class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")
        user_obj = self.model(
            email=self.normalize_email(email),
            full_name=full_name
        )
        user_obj.set_password(password)  # change user password
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # can login
    staff = models.BooleanField(default=False)  # staff user non superuser
    admin = models.BooleanField(default=False)  # superuser
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'  # username
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = []  # ['full_name'] #python manage.py createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        # does my object have a timestamp in here
        end_range = now
        return self.filter(
            activated=False,
            forced_expired=False
        ).filter(
            timestamp__gt=start_range,
            timestamp__lte=end_range
        )


class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        return self.get_queryset().filter(
            Q(email=email) |
            Q(user__email=email)
        ).filter(
            activated=False
        )


class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)  # 7 Days
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()  # 1 object
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            # pre activation user signal
            user = self.user
            user.is_active = True
            user.save()
            # post activation signal for user
            self.activated = True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', 'https://www.minloans.com.ng')
                key_path = reverse("account:email-activate", kwargs={'key': self.key})  # use reverse
                path = "{base}{path}".format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)
                subject = 'Minloansng 1-Click Email Verification'
                from_email = email_settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]
                sg = SendGridAPIClient(email_settings.SENDGRID_API_KEY)
                message = Mail(
                    from_email=from_email,
                    to_emails=recipient_list,
                    subject=subject,
                    html_content=html_
                )
                return sg.send(message)
        return False


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "profile/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


ROLE_CHOICES = (
    ('Admin', 'Admin'),
    ('Staff', 'Staff'),
    ('Customer', 'Customer'),
)

PAYMENT_PLAN = (
    ('FREEMIUM', 'FREEMIUM'),
    ('STARTUP', 'STARTUP'),
    ('BUSINESS', 'BUSINESS'),
    ('COMPANY', 'COMPANY'),
    ('ENTERPRISE', 'ENTERPRISE'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(blank=True, null=True)
    image = CloudinaryField(upload_image_path, null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    trial_days = models.DateTimeField(default=get_trial_days)
    token = models.CharField(max_length=300, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Admin", blank=True, null=True)
    plan = models.CharField(max_length=20, choices=PAYMENT_PLAN, default="FREEMIUM", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profile"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        unique_together = ('phone', 'slug')

    def __str__(self):
        return str(self.user.email)

    def get_absolute_url(self):
        return reverse('account:profile-detail', kwargs={'slug': self.slug})

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="100" height="100" />' % self.image.url)

    image_tag.short_description = 'Profile Image'
    image_tag.allow_tags = True

    def get_name(self):
        if self.user.full_name:
            caps_initials = "{}".format(self.user.full_name)
            caps_initials = caps_initials.title()
            return caps_initials
        return self.user.email

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        return "https://img.icons8.com/officel/2x/user.png"


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)


pre_save.connect(pre_save_email_activation, sender=EmailActivation)


def post_save_user_create_reciever(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation()
        Profile.objects.create(user=instance, slug=unique_slug_generator(instance), token=random_string_generator(45))


post_save.connect(post_save_user_create_reciever, sender=User)


class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

