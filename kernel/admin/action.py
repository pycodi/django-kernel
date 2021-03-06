from django.contrib import admin

from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext

from kernel.forms import action as kfaction


def move_to_group(modeladmin, request, queryset):
    form = None
    if 'apply' in request.POST:
        form = kfaction.ActionChangeGroupForm(request.POST)
        if form.is_valid():
            pass
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = kfaction.ActionChangeGroupForm(
            initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    context = {'path': request.get_full_path(), 'items': queryset, 'form': form, 'title': 'Изменение категории'}
    return render_to_response('kernel/admin/action/move_to_group.html', context, context_instance=RequestContext(request))

move_to_group.short_description = "Изменить группу"