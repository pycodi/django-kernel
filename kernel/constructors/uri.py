from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
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
from django.contrib.contenttypes.models import ContentType


class KernelUriModel(object):
    @classmethod
    def get_uri_create(cls):
        from django.conf.urls import url
        fields = cls.list_fields()
        return url(r'^%s/new.html$' % cls.get_alias(),
                   cls.get_create_view_class().as_view(), name='{0}_create'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_update(cls):
        return url(r'^%s/(?P<pk>\d+)/edit/$' % cls.get_alias(),
                   cls.get_update_view_class().as_view(), name='{0}_update'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_delete(cls):
        return url(r'^%s/(?P<pk>\d+)/delete/' % cls.get_alias(),
                   cls.get_delete_view_class().as_view(), name='{0}_delete'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_detail(cls, pk: str, format: str = '.html'):
        return url(r'^%s/(?P<%s>[a-zA-Z0-9_A-Яа-я-]{1,300})%s$' % (cls.get_alias(), cls.URI,
                                                                   (
                                                                   cls.URI_FORMAT_DETAIL if cls.URI_FORMAT_DETAIL else format)),
                   cls.get_detail_view_class().as_view(), name='{0}_view'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_list(cls):
        return url(r'^%s/$' % cls.get_alias().lower(),
                   cls.get_list_view_class().as_view(), name='{0}_list'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_export(cls):
        return url(r'^%s/export/' % cls.get_alias(),
                   cls.get_export_view_class().as_view(), name='{0}_export'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_detail_export(cls):
        return url(r'^%s/(?P<pk>\d+)/export/' % cls.get_alias(),
                   cls.get_detail_export_view_class().as_view(),
                   name='{0}_detail_export'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_crud(cls):
        import re
        uri_list = []
        for m in cls.methods():
            if re.match('get_uri_', m) and not m == 'get_uri_crud':
                uri_list.append(getattr(cls, m)())
        return uri_list