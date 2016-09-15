from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group


class ActionChangeGroupForm(forms.Form):
    group = forms.ModelChoiceField(label=_('Группа'), queryset=Group.objects.all())