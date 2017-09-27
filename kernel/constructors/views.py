from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, ListView
from django.http.response import HttpResponse
from kernel.views.kernel import KernelViewSetMixin, KernelDispachMixin

import csv


class KernelViewsModel(object):

    @classmethod
    def get_create_view_class(cls):

        return KernelViewSetMixin.create_class_form(cls)

    @classmethod
    def get_update_view_class(cls):

        return KernelViewSetMixin.update_class_form(cls)

    @classmethod
    def get_delete_view_class(cls):

        class Delete(KernelDispachMixin, DeleteView):
            model = cls
            can_action = cls.can_action_delete
            success_url = reverse_lazy('{}:{}_list'.format(cls._meta.app_label, str(cls.__name__).lower()))
            fields = cls.list_fields()

            def get_template_names(self):
                names = super(Delete, self).get_template_names()
                names.append("%s/layout/%s.html" % (cls._meta.app_label, self.template_name_suffix))
                return names

        return Delete

    @classmethod
    def get_detail_export_view_class(cls):

        class ClassView(KernelDispachMixin, DetailView):
            model = cls
            can_action = cls.can_action_view_detail

        return ClassView

    @classmethod
    def get_detail_view_class(cls):

        class ClassView(KernelDispachMixin, DetailView):
            model = cls
            can_action = cls.can_action_view_detail

        return ClassView

    @classmethod
    def get_list_view_class(cls):

        class ClassView(KernelDispachMixin, ListView):
            model = cls
            can_action = cls.can_action_view_list
            paginate_by = 100

        return ClassView

    @classmethod
    def get_export_view_class(cls):

        class ClassView(ListView):
            model = cls

            def get(self, request, *args, **kwargs):
                if not self.model.can_action_view_list(request):
                    if not request.user.is_authenticated():
                        return redirect(settings.LOGIN_URL)
                    raise PermissionDenied

                queryset_list = cls.filter_class()(self.request.GET, queryset=self.get_queryset())
                export = self.model.get_export_class()().export(queryset_list)

                export_type = self.request.GET.get('export', 'csv')
                if 'csv' in export_type:
                    response = HttpResponse(content_type='text/csv')
                elif 'xlsx' in export_type:
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                else:
                    response = HttpResponse(content_type='text/csv')

                filename = slugify(cls.get_alias())
                if cls._meta.verbose_name:
                    filename = slugify(cls._meta.verbose_name)
                response['Content-Disposition'] = 'attachment; filename="%s.%s"' % (filename, export_type)
                response.write(export.__getattribute__(export_type))
                return response

        return ClassView
