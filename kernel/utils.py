from django.conf import settings as django_settings
from django.contrib.auth import get_user_model, load_backend, login, logout

from slugify import slugify as aw_slugify

import logging


def slugify(str):
    return aw_slugify(str.lower())


def upload_dir(instance, filename):
    return '{1}/{0}'.format(filename, str(instance.__class__.__name__).lower())


def login_as(user, request, store_original_user=True):
    """
    Utility function for forcing a login as specific user -- be careful about
    calling this carelessly :)
    """
    # Save the original user pk before it is replaced in the login method
    original_user_pk = request.user.pk
    username_field = get_user_model().USERNAME_FIELD

    # Find a suitable backend.
    if not hasattr(user, 'backend'):
        for backend in django_settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    # Log the user in.
    if hasattr(user, 'backend'):
        login(request, user)
    else:
        return

