from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
# Import over module
from polymorphic.models import PolymorphicModel
from stdimage.models import StdImageField
from templated_email import send_templated_mail, get_templated_mail
from rest_framework import serializers
# Import kernel module
from kernel.constant import Lang
from kernel.managers.user import EmailUserMixinManager
from kernel.utils import upload_dir, slugify
from kernel.models.base import KernelModel
from kernel import filters as kf



import django_filters


@python_2_unicode_compatible
class KernelUser(PolymorphicModel, AbstractBaseUser, PermissionsMixin, KernelModel):
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
    birth_int = models.PositiveIntegerField(null=True, blank=True, editable=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    is_staff = models.BooleanField(_('staff status'), default=False, help_text=Lang.MU_AH2)
    is_active = models.BooleanField(_('active'), default=True, help_text=Lang.MU_AH3)
    is_emailing = models.BooleanField(_('Is emailing'), default=True)

    photo = StdImageField(upload_to=upload_dir, blank=True,
                          variations={'promotion': (775, 775, True),
                                      'large': (600, 600),
                                      'thumbnail': (75, 75, True),
                                      'medium': (300, 300)})

    objects = EmailUserMixinManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    REST = True
    ADMIN = True
    MODELFORM = True
    ROUTE_NAME = 'users'

    class Meta:
        db_table = 'krn_user'
        verbose_name = _('пользователи')
        verbose_name_plural = _('пользователи')
        swappable = 'AUTH_USER_MODEL'
        ordering = ['-last_name', ]

    def save(self, *args, **kwargs):
        if self.date_birth:
            self.birth_int = int(self.date_birth.timetuple().tm_yday)
        super().save(*args, **kwargs)

    @property
    def name(self):
        if self.first_name:
            return '{}'.format(str(' '.join([self.last_name, self.first_name, self.middle_name])).strip())
        else:
            return self.email

    def get_full_name(self):
        """ Return the email """
        return self.email

    def get_short_name(self):
        """  Return the email """
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """  Send an email to this User. """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_email(self, template, context={}, **kwargs):
        from django.conf import settings
        if self.is_emailing:
            if settings.SEND_EMAIL:
                send_templated_mail(template_name=template, from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=[self.email], context=context, **kwargs)
            else:
                send_templated_mail(template_name=template, from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=settings.DEBUG_EMAIL, context=context, **kwargs)

    @classmethod
    def get_admin_class(cls):
        from kernel.admin.kernel import KernelUserAdmin
        return KernelUserAdmin

    @staticmethod
    def list_display():
        return 'email', 'last_name', 'first_name', 'middle_name', 'phone', 'date_birth', 'is_active'

    @staticmethod
    def list_fieldsets():
        return (
           (None, {'fields': ('email', 'is_emailing', 'password')}),
           (_('Personal info'), {'fields': ('first_name', 'last_name', 'middle_name', 'date_birth', 'photo')}),
           (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
           (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

    @classmethod
    def serializer_data(cls):
        return 'id', 'email', 'external_id', 'last_name', 'first_name', 'middle_name', 'phone', 'date_birth', 'photo'

    @classmethod
    def get_serializer_class(cls):
        from kernel.fields import StdImageFieldSerializer

        class KernelUserSerializer(serializers.ModelSerializer):
            get_name = serializers.CharField(source='name')
            detail_url = serializers.CharField(source='get_absolute_url')
            photo = StdImageFieldSerializer()

            class Meta:
                model = cls
                fields = cls.serializer_data() + ('get_name', 'detail_url')

        return KernelUserSerializer

    @classmethod
    def get_filter_class(cls):
        class FilterClass(django_filters.FilterSet):
            id_list = kf.ListFilter(name='id')

            class Meta:
                model = cls
                fields = ('id', 'email', 'external_id', 'last_name', 'first_name', 'middle_name', 'date_birth')
        return FilterClass

    @classmethod
    def get_rest_viewset(cls):
        from kernel.rest import viewsets as rv
        from rest_framework.decorators import detail_route, list_route
        from rest_framework.response import Response
        from rest_framework.decorators import detail_route
        from rest_framework.exceptions import MethodNotAllowed, PermissionDenied

        class ViewSet(rv.KernelViewSets):
            queryset = cls.objects.all()
            serializer_class = cls.get_serializer_class()
            filter_class = cls.get_filter_class()
            list_serializer_class = cls.get_serializer_class()

            def get_queryset(self):
                queryset = super(ViewSet, self).get_queryset()
                return queryset.filter(id__gt=1)

            @detail_route()
            def get_permission(self, request, pk=None):
                user = cls.objects.get(pk=pk)
                if not user.id == request.user.id:
                     raise PermissionDenied
                user_serializer_class = user.get_serializer_class()
                return Response({'profile': user_serializer_class(user).data,
                                 'permissions': dict(all=user.get_all_permissions(), group=user.get_group_permissions())})
        return ViewSet

    @classmethod
    def get_update_view_class(cls):
        from kernel.views.user import KernelUserUpdateMixin
        return KernelUserUpdateMixin.update_form_class(cls)