from django.db import models

from kernel import models as km
from kernel.middleware import CrequestMiddleware


class ActionKernelModel(models.Model):

    class Meta:
        abstract = True

    @property
    def action_user(self):
        try:
            user = km.KernelUser.objects.get(email=CrequestMiddleware.get_user())
        except:
            user = km.KernelUser.objects.get(id=1)
        return user

    def generate_perm(self, action):
        app_label = self._meta.app_label
        class_name = str(self.__class__.__name__).lower()
        return '{}.{}_{}'.format(app_label, action, class_name)

    def can_action_delete(self):
        return self.action_user.has_perm(self.generate_perm('delete'))
