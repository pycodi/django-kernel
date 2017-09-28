from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
# Import kernel module
from kernel.middleware import CrequestMiddleware
from kernel import filters as kf
from kernel import constructors as kc

import uuid
import re

__all__ = [
    'KernelByModel', 'KernelModel'
]


@python_2_unicode_compatible
class KernelModel(kc.ActionKernelModel, kc.KernelPermalinkModel, kc.KernelViewsModel,
                  kc.KernelSerializerModel, kc.KernelUriModel, models.Model):

    external_id = models.CharField(_('Внешний ключ'), max_length=120, editable=False, default=uuid.uuid4)
    created_date = models.DateTimeField(_('Создан'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Изменен'), auto_now=True)

    ROUTE_NAME = 'kernel'
    REST = False
    ADMIN = False
    ALIAS = False
    EXPORT = False
    MODELFORM = False
    MODELFORM_SUBMIT = None
    URI_FORMAT_DETAIL = None

    class Meta:
        abstract = True

    @classmethod
    def admin_class(cls):
        from kernel.admin.kernel import BaseAdmin
        return type("{}Admin".format(cls.__name__), (BaseAdmin, ), {})

    def get_content_type(self):
        return ContentType.objects.get_for_model(self)

    def json_format(self):
        return self.serializer_class_list()(self).data

    def get_verbose_name(self, _name):
        return self._meta.get_field(_name).verbose_name

    @classmethod
    def get_export_class(cls):
        from import_export import resources
        from import_export import fields

        class Resource(resources.ModelResource):
            class Meta:
                model = cls
                fields = cls.export_data()
        return Resource

    @classmethod
    def get_crispy_fieldset(cls):
        return None

    @classmethod
    def get_modelform_widgets(cls):
        return None

    @classmethod
    def get_modelform_class(cls):
        if 'crispy_forms' in settings.INSTALLED_APPS and cls.MODELFORM:
            from django import forms
            from crispy_forms.helper import FormHelper
            from crispy_forms.layout import Submit, Button

            class Form(forms.ModelForm):
                class Meta:
                    model = cls
                    fields = cls.list_fields()
                    if cls.get_modelform_widgets():
                       widgets = cls.get_modelform_widgets()

                def __init__(self, *args, **kwargs):
                    super(Form, self).__init__( *args, **kwargs)
                    self.helper = FormHelper()
                    self.helper.form_class = 'form-vertical'
                    self.helper.is_multipart = True
                    self.helper.form_action = '#'
                    self.helper.add_input(Button('back',  _('Отменить'), css_class='btn', onclick="window.history.back();"))
                    self.helper.add_input(Submit('submit', (_('Сохранить') if not cls.MODELFORM_SUBMIT else cls.MODELFORM_SUBMIT), css_class='btn'))
                    if cls.get_crispy_fieldset():
                        self.helper.layout = cls.get_crispy_fieldset()
            return Form
        return None

    @classmethod
    def router_api(cls):
        return r'{1}/{0}'.format(str(cls.__name__).lower(), cls.ROUTE_NAME)

    @classmethod
    def base_name(cls):
        return 'api-{1}-{0}'.format(str(cls.__name__).lower(), cls.ROUTE_NAME)

    @classmethod
    def filters_data(cls):
        return cls.serializer_data()

    @classmethod
    def export_data(cls):
        return cls.serializer_data()

    @classmethod
    def list_fields(cls):
        return '__all__'

    @classmethod
    def list_display(cls):
        return [f.name for f in cls._meta.get_fields() if not f.related_model]

    @classmethod
    def filter_class(cls):
        import rest_framework_filters as filters

        class FilterClass(filters.FilterSet):
            id_list = kf.ListFilter(name='id')

            class Meta:
                model = cls
                fields = cls.filters_data()
                filter_overrides = {
                    models.FileField: {
                        'filter_class': django_filters.CharFilter,
                        'extra': lambda f: {
                            'lookup_expr': 'icontains',
                        },
                    },
                    models.ImageField: {
                        'filter_class': django_filters.CharFilter,
                        'extra': lambda f: {
                            'lookup_expr': 'icontains',
                        },
                    },
                }

        return FilterClass

    @classmethod
    def get_alias(cls):
        if cls.ALIAS:
            return cls.ALIAS
        return str(cls.__name__).lower()

    @classmethod
    def urls(cls):
        uri_list = []
        for m in [x for x in dir(cls)]:
            if re.match('get_uri_', m) and not m == 'get_uri_crud':
                uri_list.append(getattr(cls, m)())
        return uri_list

    @classmethod
    def get_namespace(cls):
        return cls._meta.app_label

    @classmethod
    def get_model_name(cls):
        return cls._meta.model_name


@python_2_unicode_compatible
class KernelByModel(KernelModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Создал'), on_delete=models.PROTECT,
                                   related_name="kernel_%(class)s_created_by", blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Изменил'),
                                   editable=False, related_name="kernel_%(class)s_modified_by", blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created_by:
            try:
                user = CrequestMiddleware.get_user()
                self.created_by = user
            except:
                 pass
        if not self.modified_by:
            try:
                user = CrequestMiddleware.get_user()
                self.modified_by = user
            except:
                pass
        super(KernelByModel, self).save(*args, **kwargs)

    @classmethod
    def list_display(cls):
        return 'id', 'external_id', 'created_by'








