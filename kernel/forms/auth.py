from django import forms, VERSION as DJANGO_VERSION
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField, ReadOnlyPasswordHashWidget,
    PasswordResetForm as OldPasswordResetForm,
    UserChangeForm as DjangoUserChangeForm,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.html import format_html

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

User = get_user_model()


class AuthenticationForm():
    pass
