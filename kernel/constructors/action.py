from typing import Type
from kernel.middleware import CrequestMiddleware


_cls = Type('KernelModel', bound='kernel.models.base.KernelModel')


class ActionKernelModel(object):

    @property
    def action_user(self):
        return CrequestMiddleware.get_user()

    @classmethod
    def generate_perm(cls: _cls, action):
        app_label = cls._meta.app_label
        class_name = cls._meta.model_name
        return '{}.{}_{}'.format(app_label, action, class_name)

    @classmethod
    def can_action_create(cls, request):
        return request.user.has_perm(cls.generate_perm('add'))

    @classmethod
    def can_action_update(cls, request):
        return request.user.has_perm(cls.generate_perm('change'))

    @classmethod
    def can_action_delete(cls, request):
        return request.user.has_perm(cls.generate_perm('delete'))

    @classmethod
    def can_action_view_detail(cls, request):
        return request.user.has_perm(cls.generate_perm('view'))

    @classmethod
    def can_action_view_list(cls, request):
        return request.user.has_perm(cls.generate_perm('view'))

    @classmethod
    def can_action_export(cls, request):
        return request.user.has_perm(cls.generate_perm('view'))

    def can_object_action_create(self):
        return self.action_user.has_perm(self.generate_perm('create'))

    def can_object_action_update(self):
        return self.action_user.has_perm(self.generate_perm('change'))

    def can_object_action_delete(self):
        return self.action_user.has_perm(self.generate_perm('delete'))
