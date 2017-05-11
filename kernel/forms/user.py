from django.contrib.auth.forms import (AdminPasswordChangeForm, UserChangeForm, UserCreationForm, ReadOnlyPasswordHashField)
from django.utils.translation import ugettext_lazy as _
from django import forms

from kernel import models as km


class KernelUserChangeForm(UserChangeForm):
    class Meta:
        model = km.KernelUser
        fields = '__all__'


class KernelAdminPasswordChangeForm(AdminPasswordChangeForm):
    class Meta:
        model = km.KernelUser


class KernelUserCreationForm(UserCreationForm):
    class Meta:
        model = km.KernelUser
        fields = ("email", )


class UserUpdateViewForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"/password/change/\">this form</a>."))
    class Meta:
        model = km.KernelUser
        fields = ('email', 'password', 'last_name', 'first_name', 'middle_name', 'phone', 'date_birth', 'photo')


class UserUpdateFormMixin(object):

    @staticmethod
    def model_form(_cls, _list_field):

        class UserUpdateViewForm(forms.ModelForm):
            password = ReadOnlyPasswordHashField(label=_("Password"),
            help_text=_("Raw passwords are not stored, so there is no way to see "
                        "this user's password, but you can change the password "
                        "using <a href=\"/password/change/\">this form</a>."))

            class Meta:
                model = _cls
                fields = _list_field if _list_field else ('email', 'password', 'last_name', 'first_name', 'middle_name', 'phone', 'date_birth', 'photo')

        return UserUpdateViewForm
