from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, resolve_url
from django.utils.functional import lazy
from django.conf import settings
from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (SetPasswordForm, PasswordChangeForm, PasswordResetForm)
from django.contrib.auth.tokens import default_token_generator
from django.contrib import auth
from django.utils.http import base36_to_int, is_safe_url
from django.utils import six
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView, RedirectView
from django.contrib.auth import update_session_auth_hash
from django.contrib import auth
from django.views.generic import CreateView, TemplateView, FormView, RedirectView
from django.contrib.auth.forms import (AuthenticationForm, SetPasswordForm,
                                       PasswordChangeForm, PasswordResetForm)
from braces.forms import UserKwargModelFormMixin

from .mixin import LoginRequiredMixin, WithNextUrlMixin, AuthDecoratorsMixin, CsrfProtectMixin

User = get_user_model()


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


class PasswordResetView(CsrfProtectMixin, FormView):
    template_name = 'kernel/password_reset_form.html'
    token_generator = default_token_generator
    success_url = reverse_lazy('kernel:password_reset_done')
    domain_override = None
    subject_template_name = 'registration/password_reset_subject.txt'
    email_template_name = 'registration/password_reset_email.html'
    html_email_template_name = None
    from_email = None
    form_class = PasswordResetForm

    def form_valid(self, form):
        form.save(
            domain_override=self.domain_override,
            subject_template_name=self.subject_template_name,
            email_template_name=self.email_template_name,
            token_generator=self.token_generator,
            from_email=self.from_email,
            request=self.request,
            use_https=self.request.is_secure(),
            html_email_template_name=self.html_email_template_name,
        )
        return super(PasswordResetView, self).form_valid(form)





class PasswordChangeView(LoginRequiredMixin, WithNextUrlMixin, AuthDecoratorsMixin, FormView):
    template_name = 'registration/password_change_form.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs

    def get_user(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super(PasswordChangeView, self).form_valid(form)


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/password_change_done.html'


# 4 views for password reset:
# - PasswordResetView sends the mail
# - PasswordResetDoneView shows a success message for the above
# - PasswordResetConfirmView checks the link the user clicked and
#   prompts for a new password
# - PasswordResetCompleteView shows a success message for the above




class PasswordResetDoneView(TemplateView):
    template_name = 'kernel/password_reset_done.html'


class PasswordResetConfirmView(AuthDecoratorsMixin, FormView):
    template_name = 'registration/password_reset_confirm.html'
    token_generator = default_token_generator
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, *args, **kwargs):
        assert self.kwargs.get('token') is not None
        self.user = self.get_user()
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return User._default_manager.all()

    def get_user(self):
        # django 1.5 uses uidb36, django 1.6 uses uidb64
        uidb36 = self.kwargs.get('uidb36')
        uidb64 = self.kwargs.get('uidb64')
        assert bool(uidb36) ^ bool(uidb64)
        try:
            if uidb36:
                uid = base36_to_int(uidb36)
            else:
                # urlsafe_base64_decode is not available in django 1.5
                from django.utils.http import urlsafe_base64_decode
                uid = urlsafe_base64_decode(uidb64)
            return self.get_queryset().get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def valid_link(self):
        user = self.user
        return user is not None and self.token_generator.check_token(user, self.kwargs.get('token'))

    def get_form_kwargs(self):
        kwargs = super(PasswordResetConfirmView, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(PasswordResetConfirmView, self).get_context_data(**kwargs)
        if self.valid_link():
            kwargs['validlink'] = True
        else:
            kwargs['validlink'] = False
            kwargs['form'] = None
        return kwargs

    def form_valid(self, form):
        if not self.valid_link():
            return self.form_invalid(form)
        self.save_form(form)
        return super(PasswordResetConfirmView, self).form_valid(form)

    def save_form(self, form):
        return form.save()


class PasswordResetConfirmAndLoginView(PasswordResetConfirmView):
    #success_url = resolve_url(settings.LOGIN_REDIRECT_URL)

    def save_form(self, form):
        ret = super(PasswordResetConfirmAndLoginView, self).save_form(form)
        user = auth.authenticate(username=self.user.get_username(),
                                 password=form.cleaned_data['new_password1'])
        auth.login(self.request, user)
        return ret


class PasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'
    login_url = settings.LOGIN_URL

    def get_login_url(self):
        return resolve_url(self.login_url)

    def get_context_data(self, **kwargs):
        kwargs = super(PasswordResetCompleteView, self).get_context_data(**kwargs)
        kwargs['login_url'] = self.get_login_url()
        return kwargs