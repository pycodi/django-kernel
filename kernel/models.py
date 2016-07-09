from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from polymorphic.models import PolymorphicModel

from .constant import Lang
from kernel.managers.user import PortalEmailUserMixinManager
from kernel.middleware import CrequestMiddleware


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
class KernelUser(PolymorphicModel, AbstractBaseUser, KernelPermissions):
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
    external_id = models.CharField(max_length=120, editable=False)
    email = models.EmailField(_('email'), max_length=255, unique=True, db_index=True)
    last_name = models.CharField(_('Фамилия'), max_length=30, blank=True)
    first_name = models.CharField(_('Имя'), max_length=30, blank=True)
    middle_name = models.CharField(_('Отчество'), max_length=30, blank=True)

    phone = models.CharField(_('Телефон'), max_length=30, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(_('Фотография'), null=True, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False, help_text=Lang.MU_AH2)
    is_active = models.BooleanField(_('active'), default=True, help_text=Lang.MU_AH3)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = PortalEmailUserMixinManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    REST = True
    ADMIN = True

    class Meta:
        db_table = 'krn_user'
        verbose_name = _('пользователи')
        verbose_name_plural = _('пользователи')
        swappable = 'AUTH_USER_MODEL'

    @property
    def name(self):
        return str(' '.join([self.last_name, self.first_name, self.middle_name])).strip()

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
    def router_api(cls):
        return r'users/{0}'.format(str(cls.__name__).lower())

    @classmethod
    def base_name(cls):
        return 'api-users-{0}'.format(str(cls.__name__).lower())

    @staticmethod
    def get_serializer_class():
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
        return False


@python_2_unicode_compatible
class KernelModel(models.Model):
    external_id = models.CharField(_('External Code'), max_length=120, editable=False, default=uuid.uuid4)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    REST = False
    ADMIN = False

    class Meta:
        abstract = True

    @classmethod
    def get_admin_class(cls):
        from kernel.admin.kernel import BaseAdmin

        class Admin(BaseAdmin):
            pass
        return Admin

    @classmethod
    def router_api(cls):
        return r'kernel/{0}'.format(str(cls.__name__).lower())

    @classmethod
    def base_name(cls):
        return 'api-kernel-{0}'.format(str(cls.__name__).lower())

    @classmethod
    def serializer_data(cls):
        return [f.name for f in cls._meta.get_fields()]

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
        return False

    @classmethod
    def get_detail_view_class(cls):
        from django.views.generic import DetailView

        class ClassView(DetailView):
            model = cls
        return ClassView

    @classmethod
    def get_list_view_class(cls):
        from django.views.generic import ListView

        class ClassView(ListView):
            model = cls

        return ClassView


@python_2_unicode_compatible
class KernelByModel(KernelModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Создан'),
           editable=False, related_name="kernel_%(class)s_created_by", blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Изменил'),
           editable=False, related_name="kernel_%(class)s_modified_by", blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        request = CrequestMiddleware.get_request()
        if hasattr(request, '_cached_user'):
            user = KernelUser.objects.get(email=CrequestMiddleware.get_request()._cached_user)
            if not self.created_by:
                self.created_by = user
            if not self.modified_by:
                self.modified_by = user
        super(KernelByModel, self).save(*args, **kwargs)

    @classmethod
    def list_display(cls):
        return 'id', 'external_id', 'created_by'










