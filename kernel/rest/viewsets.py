# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.core.cache import cache

from rest_framework import viewsets, mixins, permissions
from rest_framework.filters import DjangoObjectPermissionsFilter, OrderingFilter, SearchFilter, DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, DjangoObjectPermissions
from rest_framework.settings import api_settings
from rest_framework_extensions.cache.decorators import (cache_response)

import pprint


class BaseViewSets(object):
    list_serializer_class = False
    retrieve_serializer_class = False
    to_filter_backends = False

    @property
    def filter_backends(self):
        if hasattr(self, 'to_filter_backends'):
            if self.to_filter_backends:
                return api_settings.DEFAULT_FILTER_BACKENDS + self.to_filter_backends
        return api_settings.DEFAULT_FILTER_BACKENDS

    def get_serializer_class(self):
        if hasattr(self, 'list_serializer_class'):
            if self.list_serializer_class:
                if self.request.method == 'PUT':
                    return self.serializer_class
                if self.request.method == 'POST':
                    return self.serializer_class
                return self.list_serializer_class
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        list = super(BaseViewSets, self).list(request, *args, **kwargs)
        return list


class KernelViewSets(BaseViewSets, viewsets.ModelViewSet):

    def retrieve(self, *args, **kwargs):
        print(122)
        if hasattr(self, 'retrieve_serializer_class'):
            if self.retrieve_serializer_class:
                self.serializer_class = self.retrieve_serializer_class
        retrieve = super(KernelViewSets, self).retrieve(*args, **kwargs)
        return retrieve


class KernelReadOnlyViewSets(BaseViewSets, viewsets.ReadOnlyModelViewSet):
    pass


class AnyViewSet(KernelViewSets):
    """
      Простой класс управления сереализации, предназначен для простых моделей
    """
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]


class AnyViewReadOnlySet(viewsets.ReadOnlyModelViewSet):
    """
      Простой класс управления сереализцаии, доступный только на чтение и предназначеный для простых моделей
    """
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]


class ReadOnlyListModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
      Класс разграничивающий права доступа и методы фильтрации данных для API.
    """
    permission_classes = (DjangoModelPermissions, DjangoObjectPermissions)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]


class ModelViewSet(viewsets.ModelViewSet):
    """
      Простой класс управления сереализцаии, предназначен для простых моделей
    """
    permission_classes = (DjangoModelPermissions, DjangoObjectPermissions)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

