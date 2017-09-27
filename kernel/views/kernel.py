from __future__ import unicode_literals
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, resolve_url
from django.views.generic import ListView

from django_tables2.views import SingleTableMixin
from django_filters.views import BaseFilterView
from urllib import parse


import itertools


class KernelDispachMixin(object):
    can_action = False

    def dispatch(self, request, *args, **kwargs):
        if self.can_action:
            if not self.can_action(request):
                if not request.user.is_authenticated():
                    response = redirect(settings.LOGIN_URL)
                    response['Location'] += '?next={}'.format(self.request.path)
                    return response
                raise PermissionDenied
        return super(KernelDispachMixin, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        names = super().get_template_names()
        names.append("{0}/{1}/{1}{2}.html" .format(self.model._meta.app_label, self.model._meta.model_name, self.template_name_suffix))
        return names



class KernelBaseMixin(object):
    pass


class KernelViewSetMixin(KernelBaseMixin):

    @staticmethod
    def create_class_form(_cls, _form_class=False, _form_valid_message='', _parents=[], **_kwargs):
        parents = list(itertools.chain([KernelDispachMixin, CreateView, ], _parents))

        class Create(*parents):
            model = _cls
            can_action = _cls.can_action_create
            success_url = reverse_lazy('%s:%s_list' % (_cls.get_namespace(), str(_cls.__name__).lower()))
            form_valid_message = _form_valid_message

            if _cls.get_modelform_class():
                form_class = _cls.get_modelform_class()
            else:
                fields = _cls.list_fields()

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for key, value in _kwargs.items():
                    self.__dict__[key] = value

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['class'] = _cls
                return context

        return Create

    @staticmethod
    def update_class_form(_cls, _form_class=False, _form_valid_message='', _parents=[], **_kwargs):
        _form_class = _form_class if _form_class else _cls.get_modelform_class()
        parents = list(itertools.chain([KernelDispachMixin, pdateView, ], _parents))

        class Update(*parents):
            model = _cls
            form_valid_message = _form_valid_message
            can_action = _cls.can_action_update
            if _form_class:
                form_class = _cls.get_modelform_class()
            else:
                fields = _cls.list_fields()

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for key, value in _kwargs.items():
                    self.__dict__[key] = value

            def post(self, request, *args, **kwargs):
                self.object = self.get_object()
                form = self.get_form()
                if form.is_valid():
                    return self.form_valid(form)
                else:
                    return self.form_invalid(form)

            def get(self, request, *args, **kwargs):
                self.object = self.get_object()
                if not self.object.can_object_action_update():
                    raise PermissionDenied
                return super().get(request, *args, **kwargs)

        return Update

    @staticmethod
    def list_class(_cls, _parents=None, _context={}, **_kwargs):
        parents = list(itertools.chain(
            [] if _parents is None else _parents,
            [KernelDispachMixin, BaseFilterView, SingleTableMixin, ListView])
        )

        class KernelList(*parents):
            can_action = _cls.can_action_view_list
            table_class = _cls.table_class()
            paginate_by = 200
            model = _cls
            queryset = _cls.lazy_queryset() if getattr(_cls, 'lazy_queryset', None) else _cls.objects.select_related()

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for key, value in _kwargs.items():
                    self.__dict__[key] = value

            def get_filterset_class(self):
                return _cls.filter_class()

            def get_table_data(self):
                return self.get_filterset_class()(self.request.GET, queryset=self.get_queryset())

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                table = self.get_table()
                table.hide_fields = ['', ]
                table.requests = self.request.GET
                table_cookie = self.request.COOKIES.get(str(self.request.path).replace('/', ''))
                if table_cookie:
                    table.hide_fields = eval(parse.unquote(table_cookie))
                context[self.get_context_table_name(table)] = table
                context['status'] = self.kwargs.get('status', False)
                context['model'] = _cls._meta.verbose_name
                list(map(lambda item: context.setdefault(item[0], item[1](self) if callable(item[1]) else item[1]), _context.items()))
                return context
        return KernelList

    @staticmethod
    def detail_class(_cls, _parents=[], _context={}, **_kwargs):
        parents = list(itertools.chain([] if _parents is None else _parents, [KernelDispachMixin, DetailView]))

        class KernelDetail(*parents):
            model = _cls
            queryset = _cls.lazy_queryset() if getattr(_cls, 'lazy_queryset', None) else _cls.objects.select_related()
            can_action = _cls.can_action_view_detail

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for key, value in _kwargs.items():
                    self.__dict__[key] = value

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['model'] = context.get('object')._meta.verbose_name
                list(map(lambda item: context.setdefault(item[0], item[1](self) if callable(item[1]) else item[1]), _context.items()))
                return context
        return KernelDetail
