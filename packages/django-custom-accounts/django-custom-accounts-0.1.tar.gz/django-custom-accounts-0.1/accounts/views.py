# -*- coding: utf-8 -*-

"""
    Custom Accounts Views
    Author  :   Alvaro Lizama Molina <nekrox@gmail.com>
"""

from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.sites.models import get_current_site
from django.contrib.auth import login, get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template import loader
from .settings import CUSTOM_AUTH_REGISTER_REDIRECT_URL, CUSTOM_AUTH_ACTIVATION_EMAIL
from .settings import CUSTOM_AUTH_AUTO_LOGIN, CUSTOM_AUTH_CONFIRM_REDIRECT_URL
from .forms import CustomUserCreationForm


@csrf_protect
def register(request, template_name='registration/register_form.html',
                   email_template_name='registration/activation_email.html',
                   subject_template_name='registration/activation_subject.txt',
                   register_form=CustomUserCreationForm,
                   token_generator=default_token_generator,
                   post_register_redirect=CUSTOM_AUTH_REGISTER_REDIRECT_URL,
                   domain_override=None,
                   use_https=False,
                   from_email=None,
                   current_app=None,
                   extra_context=None):

    if request.method == "POST":
        form = register_form(request.POST)
        if form.is_valid():
            user = form.save()

            if CUSTOM_AUTH_ACTIVATION_EMAIL:

                if not domain_override:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                else:
                    site_name = domain = domain_override

                c = {
                    'email': user.email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user_full_name': user.get_full_name(),
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',
                }
                subject = loader.render_to_string(subject_template_name, c)
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, from_email, [user.email])
            else:
                user.is_active = True
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                user.save()
                if CUSTOM_AUTH_AUTO_LOGIN:
                    login(request, user)

            if post_register_redirect is not None:
                return HttpResponseRedirect(post_register_redirect)
    else:
        form = register_form()

    context = {
        'form': form,
    }

    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def activation_confirm(request, template_name='registration/activation_confirm.html',
                    uidb64=None, token=None,
                    token_generator=default_token_generator,
                    post_confirm_redirect=CUSTOM_AUTH_CONFIRM_REDIRECT_URL,
                    current_app=None, extra_context=None):

    UserModel = get_user_model()
    assert uidb64 is not None and token is not None

    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        user.is_active = True
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        if CUSTOM_AUTH_AUTO_LOGIN:
            login(request, user)
        if post_confirm_redirect is not None:
            return HttpResponseRedirect(post_confirm_redirect)
    else:
        validlink = False

    context = {
        'validlink': validlink,
    }

    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
