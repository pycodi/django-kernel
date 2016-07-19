from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)

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
        fields = ("email",)