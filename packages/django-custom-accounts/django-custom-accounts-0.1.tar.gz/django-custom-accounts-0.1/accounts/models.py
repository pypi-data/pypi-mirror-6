# -*- coding: utf-8 -*-

"""
    Custom Accounts Model
    Author  :   Alvaro Lizama Molina <nekrox@gmail.com>
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        email =  CustomUserManager.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class AbstractCustomUser(AbstractBaseUser, PermissionsMixin):

    """Custom User Model """

    first_name = models.CharField(_('first name'), max_length=512, default='',
            null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=512, default='',
            null=True, blank=True)
    email = models.EmailField(_('email address'), max_length=255,
                              unique=True, db_index=True)
    is_staff = models.BooleanField(_('staff status'), default=False, blank=True,
            help_text=_('Designates whether the user can log into this admin '
                        'site.'))
    is_active = models.BooleanField(_('active'), default=False, blank=True,
            help_text=_('Designates whether this user should be treated as '
                        'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email):
        send_mail(subject, message, from_email, [self.email])


class CustomUser(AbstractCustomUser):

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['is_superuser', 'first_name']
