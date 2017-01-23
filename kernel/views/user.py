from django.views.generic import DetailView, UpdateView

from kernel.views import mixin as mixin
from kernel import forms as kf


class KernelUserUpdateMixin(object):

    @staticmethod
    def update_form_class(_cls, _form_class=None, _list_field=None):
        _cls_update_form = mixin.KernelViewSetMixin.update_class_form(_cls)

        class KernelUserUpdateView(_cls_update_form, mixin.KernelDispachMixin, UpdateView):
            model = _cls

            def get_form_class(self):
                return _form_class if _form_class else kf.UserUpdateFormMixin.model_form(_cls, _list_field)

        return KernelUserUpdateView

