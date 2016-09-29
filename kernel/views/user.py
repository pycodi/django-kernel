from django.views.generic import DetailView, UpdateView
from django.utils.translation import ugettext_lazy as _

from kernel import models as km
from kernel.views import mixin as mixin
from kernel import forms as kf


class KernelUserUpdateView(mixin.KernelDispachMixin, UpdateView):
    model = km.KernelUser
    can_action = km.KernelUser.can_action_update

    def get_form_class(self):
        return  kf.UserUpdateViewForm

