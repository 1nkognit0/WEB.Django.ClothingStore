from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from common.views import TitleMixin
from products.models import Basket
from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from users.models import EmailVerification, User


class UserLoginView(TitleMixin, LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    next_page = '/'
    title = 'Авторизация'


class UserRegistrationView(TitleMixin, SuccessMessageMixin,  CreateView):
    model = User
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')
    title = 'Регистрация'
    success_message = 'Вы успешно зарегестрированы!'


class UserProfileView(TitleMixin, UpdateView):
    model = User
    template_name = 'users/profile.html'
    form_class = UserProfileForm
    title = 'Личный кабинет'

    def get_success_url(self):
        return reverse_lazy('users:profile', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data()
        context['baskets'] = Basket.objects.filter(user=self.object)
        return context


class UserLogoutView(LogoutView):
    next_page = '/'


class UserEmailVerification(TitleMixin, TemplateView):
    title = 'Подтверждение почты'
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verify = EmailVerification.objects.filter(code=code, user=user)
        if email_verify.exists() and not email_verify.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(UserEmailVerification, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('users:index'))
