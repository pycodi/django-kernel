# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _

from kernel import forms as kforms


class BaseAdmin(admin.ModelAdmin):

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


class KernelUserAdmin(BaseAdmin, UserAdmin):
    """
    Базовый класс для User моделей
    """
    ordering = ('-id',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    add_form = kforms.KernelUserCreationForm
    form = kforms.KernelUserChangeForm
    change_password_form = kforms.AdminPasswordChangeForm


class KernelAdmin(BaseAdmin):
    ordering = ('-id',)



