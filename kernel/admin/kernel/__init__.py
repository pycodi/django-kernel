from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from functools import update_wrapper
from django.contrib import admin
from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text

from django.utils.html import escape
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.admin import ModelAdmin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from django.utils.translation import ugettext_lazy as _

from kernel import forms as kforms
from kernel import models as km
from kernel.admin import action as kaa
from kernel.utils import login_as





class BaseAdmin(admin.ModelAdmin):
    list_per_page = 100

    def get_fieldsets(self, request, obj=None):
        if hasattr(self.model, 'list_fieldsets'):
            return self.model.list_fieldsets()
        if self.fieldsets:
            return self.fieldsets
        return [(None, {'fields': self.get_fields(request, obj)})]

    def get_list_display(self, request):
        if hasattr(self.model, 'list_display'):
            return self.model.list_display()
        return self.list_display

    def get_list_filter(self, request):
        if hasattr(self.model, 'list_filter'):
            return self.model.list_filter()
        return self.list_filter

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'created_by'):
            if getattr(obj, 'created_by', None) is None:
                obj.created_by = request.user
        obj.save()


class KernelUserAdmin(UserAdmin):
    """
    Базовый класс для User моделей
    """
    actions = [kaa.move_to_group]
    list_per_page = 100
    ordering = ('-id',)
    list_display = km.KernelUser.list_display() + ('groups_list', 'login_as')
    fieldsets = km.KernelUser.list_fieldsets()
    add_form = kforms.KernelUserCreationForm
    form = kforms.KernelUserChangeForm
    change_password_form = kforms.AdminPasswordChangeForm

    def groups_list(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])

    def login_as(self, obj):
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.model_name
        return '<a href="{}" target="_blank">{}</a>'.format(reverse('%s:%s_%s_loginas' % info, args=(obj.pk,)), _('Перейти'))
    login_as.allow_tags = True

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            url(r'^(.+)/login_as/$', self.admin_site.admin_view(self.user_view_loginas), name='%s_%s_loginas' % info),
        ] + super(KernelUserAdmin, self).get_urls()

    def user_view_loginas(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
            })
        if request.user.is_superuser:
            login_as(user, request)
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.model_name
        return HttpResponseRedirect(reverse('%s:%s_%s_change' % info, args=(user.pk,)))


class KernelAdmin(BaseAdmin):
    ordering = ('-id',)



