from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.contrib import auth
from django.views.generic import CreateView, TemplateView, FormView, RedirectView
from django.contrib.auth.forms import (AuthenticationForm, SetPasswordForm,
                                       PasswordChangeForm, PasswordResetForm)
from braces.forms import UserKwargModelFormMixin


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = "kernel/login.html"
    success_url = '/'

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


class LogoutView(TemplateView, RedirectView):
    url = '/login/'
    permanent = True

    def get(self, *args, **kwargs):
        auth.logout(self.request)
        if self.get_redirect_url(**kwargs):
            return RedirectView.get(self, *args, **kwargs)
        else:
            return TemplateView.get(self, *args, **kwargs)