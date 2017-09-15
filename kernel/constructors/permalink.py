from django.db import models


class KernelPermalinkModel(object):

    @models.permalink
    def get_absolute_url(self):
        attr = getattr(self, self._meta.model.URI)
        return '{0}:{1}_view'.format(self.get_namespace(), self.get_model_name()), [str("%s" % attr)]

    @classmethod
    @models.permalink
    def get_absolute_create_url(cls):
        return '{0}:{1}_create'.format(cls.get_namespace(), cls.get_model_name()), []

    @models.permalink
    def get_absolute_delete_url(self):
        attr = getattr(self, self._meta.model.URI)
        return '{0}:{1}_delete'.format(self.get_namespace(), self.get_model_name()), [str("%s" % attr)]

    @models.permalink
    def get_absolute_update_url(self):
        attr = getattr(self, self._meta.model.URI)
        return '{0}:{1}_update'.format(self.get_namespace(), self.get_model_name()), [str("%s" % attr)]

    @models.permalink
    def get_absolute_export_url(self):
        attr = getattr(self, self._meta.model.URI)
        return '{0}:{1}_export'.format(self.get_namespace(), self.get_model_name()), [str("%s" % attr)]