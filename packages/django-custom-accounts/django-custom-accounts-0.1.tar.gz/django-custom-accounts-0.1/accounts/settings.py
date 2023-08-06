# -*- coding: utf-8 -*-

"""
    Custom Accounts Settings
    Author  :   Alvaro Lizama Molina <nekrox@gmail.com>
"""

from django.conf import settings


CUSTOM_AUTH_ACTIVATION_EMAIL = getattr(settings, 'CUSTOM_AUTH_ACTIVATION_EMAIL', True)
CUSTOM_AUTH_AUTO_LOGIN = getattr(settings, 'CUSTOM_AUTH_AUTO_LOGIN', True)
CUSTOM_AUTH_REGISTER_REDIRECT_URL = getattr(settings, 'CUSTOM_AUTH_REGISTER_REDIRECT_URL', None)
CUSTOM_AUTH_CONFIRM_REDIRECT_URL = getattr(settings, 'CUSTOM_AUTH_CONFIRM_REDIRECT_URL', None)
LOGOUT_REDIRECT_URL = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
