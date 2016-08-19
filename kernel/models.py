from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils.html import strip_tags
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.template.defaultfilters import truncatechars_html
from django.conf.urls import url


from polymorphic.models import PolymorphicModel
from stdimage.models import StdImageField
from ckeditor_uploader.fields import RichTextUploadingField


from .constant import Lang
from kernel.managers.user import PortalEmailUserMixinManager
from kernel.middleware import CrequestMiddleware
from kernel.utils import upload_dir, slugify
from kernel import managers as kman
from kernel import filters as kf

from rest_framework import serializers

import django_filters
import uuid


@python_2_unicode_compatible
class KernelPermissions(PermissionsMixin):
    base_objects = models.Manager()

    class Meta:
        db_table = 'krn_permissions'
        verbose_name = _('права доступа')
        verbose_name_plural = _('права доступа')


@python_2_unicode_compatible
class KernelModel(models.Model):
    external_id = models.CharField(_('External Code'), max_length=120, editable=False, default=uuid.uuid4)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    REST = False
    ADMIN = False
    ALIAS = False
    ROUTE_NAME = 'kernel'
    EXPORT = False
    URI = 'pk'

    class Meta:
        abstract = True

    @classmethod
    def get_admin_class(cls):
        from kernel.admin.kernel import BaseAdmin

        class Admin(BaseAdmin):
            pass
        return Admin

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
    def router_api(cls):
        return r'{1}/{0}'.format(str(cls.__name__).lower(), cls.ROUTE_NAME)

    @classmethod
    def base_name(cls):
        return 'api-{1}-{0}'.format(str(cls.__name__).lower(), cls.ROUTE_NAME)

    @classmethod
    def serializer_data(cls):
        return [f.name for f in cls._meta.get_fields()]

    @classmethod
    def export_data(cls):
        return cls.serializer_data()

    @classmethod
    def list_fields(cls):
        return None

    @classmethod
    def get_serializer_class(cls):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = cls
                fields = cls.serializer_data()
        return Serializer

    @classmethod
    def get_list_serializer_class(cls):
        return False

    @classmethod
    def get_filter_class(cls):
        class FilterClass(django_filters.FilterSet):
            class Meta:
                model = cls
                fields = cls.serializer_data()
        return FilterClass

    @classmethod
    def get_rest_viewset(cls):
        from kernel.rest import viewsets as rv
        from rest_framework.decorators import detail_route, list_route
        from rest_framework.response import Response

        class ViewSet(rv.KernelViewSets):
            queryset = cls.objects.all()
            serializer_class = cls.get_serializer_class()
            filter_class = cls.get_filter_class()
            list_serializer_class = cls.get_serializer_class()

            def get_queryset(self):
                queryset = super(ViewSet, self).get_queryset()
                return queryset.filter(id__gt=1)

        return ViewSet

    @classmethod
    def get_create_view_class(cls, fields_list):
        class_name = str(cls.__name__).lower()

        class Create(CreateView):
            model = cls
            success_url = reverse_lazy('%s_list' % class_name)
            fields = fields_list
        return Create

    @classmethod
    def get_update_view_class(cls, fields_list):
        class_name = str(cls.__name__).lower()

        class Update(UpdateView):
            model = cls
            success_url = reverse_lazy('%s_list' % class_name)
            fields = fields_list
        return Update

    @classmethod
    def get_delete_view_class(cls, fields_list):
        class_name = str(cls.__name__).lower()

        class Delete(DeleteView):
            model = cls
            success_url = reverse_lazy('%s_list' % class_name)
            fields = fields_list
        return Delete

    @classmethod
    def get_detail_view_class(cls):
        from django.views.generic import DetailView

        class ClassView(DetailView):
            model = cls
        return ClassView

    @classmethod
    def get_list_view_class(cls):
        from django.views.generic import ListView
#        from django_tables2 import SingleTableView

        class ClassView(ListView):
            model = cls
        return ClassView

    @classmethod
    def get_detail_export_view_class(cls):
        from django.views.generic import DetailView

        class ClassView(DetailView):
            model = cls
        return ClassView

    @classmethod
    def get_export_view_class(cls):
        from django.views.generic import TemplateView, ListView
        from django.http.response import HttpResponse
        import csv

        class ClassView(ListView):
            model = cls

            def get(self, request, *args, **kwargs):
                export_type = self.request.GET.get('export', 'csv')
                export = self.model.get_export_class()().export()
                if 'csv' in export_type:
                    response = HttpResponse(content_type='text/csv')
                elif 'xlsx' in export_type:
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                else:
                    response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="%s.%s"' % (slugify(cls.get_alias()) , export_type)
                response.write(export.__getattribute__(export_type))
                return response
        return ClassView

    @classmethod
    def get_alias(cls):
        if cls.ALIAS:
            return cls.ALIAS
        return str(cls.__name__).lower()

    @classmethod
    def get_uri_create(cls):
        from django.conf.urls import url
        fields = cls.list_fields()
        return url(r'^%s/new.html$' % cls.get_alias(),
                   cls.get_create_view_class(fields).as_view(), name='{0}_create'.format(cls.get_alias()))

    @classmethod
    def get_uri_update(cls):
        fields = cls.list_fields()
        return url(r'^%s/(?P<pk>\d+)/edit/$' %  cls.get_alias(),
                   cls.get_update_view_class(fields).as_view(), name='{0}_update'.format( cls.get_alias()))

    @classmethod
    def get_uri_delete(cls):
        fields = cls.list_fields()
        return url(r'^%s/(?P<pk>\d+)/delete/' % cls.get_alias(),
                   cls.get_delete_view_class(fields).as_view(), name='{0}_delete'.format( cls.get_alias()))

    @classmethod
    def get_uri_detail(cls, pk: str = URI):
        return url(r'^%s/(?P<%s>[a-zA-Z0-9_A-Яа-я-]{1,300}).html$' % (str(cls.__name__).lower(), pk),
                   cls.get_detail_view_class().as_view(), name='{0}_view'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_list(cls):
        return url(r'^%s/$' % cls.get_alias().lower(),
                   cls.get_list_view_class().as_view(), name='{0}_list'.format( cls.get_alias().lower()))

    @classmethod
    def get_uri_export(cls):
        return url(r'^%s/export/' % cls.get_alias(),
                   cls.get_export_view_class().as_view(), name='{0}_export'.format(cls.get_alias()))

    @classmethod
    def get_uri_detail_export(cls):
        return url(r'^%s/(?P<pk>\d+)/export/' % cls.get_alias(),
                   cls.get_detail_export_view_class().as_view(), name='{0}_detail_export'.format(cls.get_alias()))

    @classmethod
    def get_uri_crud(cls):
        return cls.get_uri_create(), cls.get_uri_update(), \
               cls.get_uri_detail(), cls.get_uri_list(), cls.get_uri_delete(), cls.get_uri_export()

    @models.permalink
    def get_absolute_url(self, pk: str = 'slug'):
        class_app = str(self._meta.app_label)
        attr = getattr(self, pk)
        return '{0}:{1}_view'.format(class_app,  self.get_alias()), [str("%s" % attr)]


@python_2_unicode_compatible
class KernelUser(PolymorphicModel, AbstractBaseUser, KernelPermissions, KernelModel):
    """
    Класс для пользователей всей системы. PortalEmailUser не имеет поля имя пользователя,
    в отличие от стандартного класса Django.

    USERNAME_FIELD = email. Use this if you need to extend EmailUser.
    Inherits from both the AbstractBaseUser and PermissionMixin.
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """
    email = models.EmailField(_('email'), max_length=255, unique=True, db_index=True)
    last_name = models.CharField(_('Фамилия'), max_length=30, blank=True)
    first_name = models.CharField(_('Имя'), max_length=30, blank=True)
    middle_name = models.CharField(_('Отчество'), max_length=30, blank=True)

    phone = models.CharField(_('Телефон'), max_length=30, blank=True)
    date_birth = models.DateField(null=True, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False, help_text=Lang.MU_AH2)
    is_active = models.BooleanField(_('active'), default=True, help_text=Lang.MU_AH3)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    photo = StdImageField(upload_to=upload_dir, blank=True,
                          variations={'promotion': (775, 775, True),
                                      'large': (600, 600),
                                      'thumbnail': (75, 75, True),
                                      'medium': (300, 300)})

    objects = PortalEmailUserMixinManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    REST = True
    ADMIN = True
    ROUTE_NAME = 'users'

    class Meta:
        db_table = 'krn_user'
        verbose_name = _('пользователи')
        verbose_name_plural = _('пользователи')
        swappable = 'AUTH_USER_MODEL'

    @property
    def name(self):
        if self.first_name:
            return str(' '.join([self.last_name, self.first_name, self.middle_name])).strip()
        else:
            return self.email

    def get_full_name(self):
        """
        Return the email.
        """
        return self.email

    def get_short_name(self):
        """
        Return the email.
        """
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_email(self, template, context = {}, **kwargs):
        from templated_email import send_templated_mail
        from django.conf import settings
        send_templated_mail(template_name=template, from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[self.email], context=context, **kwargs)

    @classmethod
    def get_admin_class(cls):
        from kernel.admin.kernel import KernelUserAdmin
        return KernelUserAdmin

    @staticmethod
    def list_display():
        return 'email', 'last_name', 'first_name', 'middle_name', 'phone', 'date_birth'

    @staticmethod
    def list_fieldsets():
        return (
           (None, {'fields': ('email', 'password')}),
           (_('Personal info'), {'fields': ('first_name', 'last_name', 'photo')}),
           (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
           (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

    @classmethod
    def serializer_data(cls):
        return 'id', 'email', 'external_id', 'last_name', 'first_name', 'middle_name', 'phone', 'date_birth', 'photo',

    @classmethod
    def get_serializer_class(cls):
        from kernel.fields import StdImageFieldSerializer

        class KernelUserSerializer(serializers.ModelSerializer):
            get_name = serializers.CharField(source='name')
            photo = StdImageFieldSerializer()

            class Meta:
                model = cls
                fields = cls.serializer_data() + ('get_name',)

        return KernelUserSerializer

    @classmethod
    def get_filter_class(cls):
        class FilterClass(django_filters.FilterSet):
            class Meta:
                model = cls
                fields = cls.serializer_data()
        return FilterClass


@python_2_unicode_compatible
class KernelByModel(KernelModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Создан'),
           editable=False, related_name="kernel_%(class)s_created_by", blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Изменил'),
           editable=False, related_name="kernel_%(class)s_modified_by", blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created_by:
            user = KernelUser.objects.get(email=CrequestMiddleware.get_user())
            self.created_by = user
        if not self.modified_by:
            user = KernelUser.objects.get(email=CrequestMiddleware.get_user())
            self.modified_by = user
        super(KernelByModel, self).save(*args, **kwargs)

    @classmethod
    def list_display(cls):
        return 'id', 'external_id', 'created_by'


@python_2_unicode_compatible
class KernelUnit(KernelByModel):
    code = models.CharField(_('Код'), max_length=255, unique=True, default=uuid.uuid4)
    name = models.CharField(_('Название'), max_length=255)

    REST = True
    ROUTE_NAME = 'unit'

    class Meta:
        abstract = True
        verbose_name = _('Списки')
        verbose_name_plural = _('Списки')

    def __str__(self):
        return self.name

    @classmethod
    def get_filter_class(cls):
        class FilterClass(django_filters.FilterSet):
            code_list = kf.ListFilter(name='code')

            class Meta:
                model = cls
                fields = cls.serializer_data() + ('code_list',)
        return FilterClass

    @classmethod
    def list_display(cls):
        return 'code', 'name', 'external_id', 'created_by', 'modified_date'

    @classmethod
    def serializer_data(cls):
        return 'id', 'code', 'name'


@python_2_unicode_compatible
class KernelPage(KernelByModel):
    HIDDEN_STATUS = -1
    DRAFT_STATUS = 0
    PUBLISHED_STATUS = 1

    STATUS_CHOICES = (
        (HIDDEN_STATUS, 'Hidden'),
        (DRAFT_STATUS, 'Draft'),
        (PUBLISHED_STATUS, 'Published')
    )

    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(_(u'Заголовок'), max_length=255)
    longtitle = models.CharField(_(u'Расширенный заголовок'), blank=True, max_length=255)
    keywords = models.CharField(_(u'Ключевые слова'), blank=True, max_length=255)
    description = models.CharField(_(u'Описание'), blank=True, max_length=255)
    slug = models.SlugField(_('URL'), help_text=_(u'Использовать в качестве урла транскрипцию ключевых слов'), max_length=120, unique=True, blank=True)
    image = StdImageField(upload_to=upload_dir, blank=True, variations={'promotion': (775, 275, True), 'large': (600, 400), 'thumbnail': (75, 75, True), 'medium': (300, 200)})
    introtext = models.TextField(verbose_name=_(u'Аннотация'))
    content = RichTextUploadingField(verbose_name=_(u'Статья'))

    status = models.IntegerField(_(u'Статус'), choices=STATUS_CHOICES, default=DRAFT_STATUS)
    comment_enabled = models.BooleanField(_('comment enabled'), default=True)

    views = models.IntegerField(default=0)

    objects = models.Manager()
    published = kman.PublishedManager()

    class Meta:
        ordering = ['-created_date']
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        cache.clear()
        obj = super(KernelPage, self).save(*args, **kwargs)
        return obj

    @classmethod
    def list_display(cls):
        return 'id',  'title', 'status',

    @property
    def word_count(self):
        return len(strip_tags(self.content))

    @property
    def get_content(self):
        return self.content

    @property
    def get_introtext(self):
        return truncatechars_html(self.introtext, 80)






