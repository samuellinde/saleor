from django.contrib.auth.hashers import (check_password, make_password,
                                         is_password_usable)
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy
from django.utils import timezone
from saleor.countries import COUNTRY_CHOICES


class Address(models.Model):
    user = models.ForeignKey('User', related_name='addressbook')
    alias = models.CharField(
        ugettext_lazy('short alias'),
        max_length=30, default=ugettext_lazy('Home'),
        help_text=ugettext_lazy(
            'User-defined alias which identifies this address'))
    first_name = models.CharField(
        ugettext_lazy('first name'), max_length=256, blank=True)
    last_name = models.CharField(
        ugettext_lazy('last name'), max_length=256, blank=True)
    company_name = models.CharField(
        ugettext_lazy('company name'), max_length=256, blank=True)
    street_address_1 = models.CharField(
        ugettext_lazy('street address 1'), max_length=256)
    street_address_2 = models.CharField(
        ugettext_lazy('street address 2'), max_length=256, blank=True)
    city = models.CharField(ugettext_lazy('city'), max_length=256)
    postal_code = models.CharField(ugettext_lazy('postal code'), max_length=20)
    country = models.CharField(
        ugettext_lazy('country'), choices=COUNTRY_CHOICES, max_length=2)
    country_area = models.CharField(
        ugettext_lazy('country administrative area'), max_length=128)
    phone = models.CharField(
        ugettext_lazy('phone number'), max_length=30, blank=True)

    class Meta:
        unique_together = ('user', 'alias')

    def __unicode__(self):
        return self.alias


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, is_staff=False,
                    is_active=True, **extra_fields):
        '''
        Creates and saves a User with the given username, email and password.
        '''
        now = timezone.now()
        email = UserManager.normalize_email(email)
        user = self.model(email=email, is_active=is_active, is_staff=is_staff,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, is_staff=True, **extra_fields)


class User(models.Model):
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(
        ugettext_lazy('staff status'), default=False)
    is_active = models.BooleanField(ugettext_lazy('active'), default=False)
    password = models.CharField(
        ugettext_lazy('password'), max_length=128, editable=False)
    date_joined = models.DateTimeField(
        ugettext_lazy('date joined'), default=timezone.now, editable=False)
    last_login = models.DateTimeField(
        ugettext_lazy('last login'), default=timezone.now, editable=False)
    default_shipping_address = models.ForeignKey(
        Address, related_name='+', null=True, blank=True)
    default_billing_address = models.ForeignKey(
        Address, related_name='+', null=True, blank=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __unicode__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, *_args, **_kwargs):
        return True

    def has_perms(self, *_args, **_kwargs):
        return True

    def has_module_perms(self, _app_label):
        return True

    def get_username(self):
        'Return the identifying username for this User'
        return self.email

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=['password'])
        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        self.password = make_password(None)

    def has_usable_password(self):
        return is_password_usable(self.password)