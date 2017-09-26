from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
# Import kernel module
from kernel import filters as kf
from .base import KernelByModel, KernelModel


import uuid


@python_2_unicode_compatible
class KernelUnit(KernelByModel):
    code = models.CharField(_('Код'), max_length=255, unique=True, default=uuid.uuid4)
    name = models.CharField(_('Название'), max_length=255)

    REST = True
    ADMIN = True
    ROUTE_NAME = 'unit'

    class Meta:
        abstract = True
        ordering = ('name', )

    def __str__(self):
        return self.name

    @classmethod
    def filter_class(cls):
        return type('{}FilterClass'.format(cls.__name__), (super().filter_class(), ), {
            'code_list':  kf.ListFilter(name='code'), 'id_list': kf.ListFilter(name='id'),
            'Meta': type('Meta', (object, ), {'model': cls, 'fields': cls.filters_data() + ('code_list', 'id_list')})})

    @classmethod
    def admin_class(cls):
        return type('{}Admin'.format(cls.__name__), (super().get_admin_class(), ), {
            'search_fields': ('code', 'name', )})

    @classmethod
    def list_display(cls):
        return 'id', 'code', 'name', 'external_id', 'created_by', 'modified_date'

    @classmethod
    def serializer_data(cls):
        return 'id', 'code', 'name', 'external_id', 'created_by', 'modified_date'

    @classmethod
    def get_rest_viewset(cls):
        from kernel.rest import viewsets as rv

        class ViewSet(rv.KernelViewSets):
            queryset = cls.objects.all().order_by('name')
            serializer_class = cls.get_serializer_class()
            filter_class = cls.filter_class()
            list_serializer_class = cls.serializer_class_list()
        return ViewSet


class KernelList(KernelModel):
    """
    Базовая модель для списков
    """
    name = models.CharField(_('Название'), max_length=255)

    REST = True
    ADMIN = True
    ROUTE_NAME = 'list'

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

