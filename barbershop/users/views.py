from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import UserLoginForm, UserRegisterForm


class UserRegisterView(CreateView):
    """
    Представление (CBV) для регистрации новых пользователей.
    """
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')  # URL для перенаправления после успешной регистрации
    
    def dispatch(self, request, *args, **kwargs):
        """
        Перенаправление аутентифицированных пользователей.
        """
        if request.user.is_authenticated:
            return redirect('landing')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Обработка валидной формы:
        - Сохранение пользователя
        - Автоматический вход
        - Добавление сообщения об успехе
        """
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Обработка невалидной формы с добавлением сообщения об ошибке.
        """
        messages.error(self.request, 'Ошибка регистрации. Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """
        Добавление дополнительного контекста для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class UserLoginView(LoginView):
    """
    Представление (CBV) для входа пользователей в систему.
    """
    template_name = 'users/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True  # Перенаправление аутентифицированных пользователей
    
    def get_success_url(self):
        """
        Определение URL для перенаправления после успешного входа.
        Учитывает параметр next.
        """
        next_url = self.request.GET.get('next')
        messages.success(self.request, 'Вы успешно вошли в систему!')
        
        if next_url:
            return next_url
        else:
            return reverse_lazy('landing')
    
    def form_invalid(self, form):
        """
        Обработка невалидной формы с добавлением сообщения об ошибке.
        """
        messages.error(self.request, 'Ошибка входа. Пожалуйста, проверьте имя пользователя и пароль.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """
        Добавление дополнительного контекста для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в аккаунт'
        return context


class UserLogoutView(LogoutView):
    """
    Представление (CBV) для выхода пользователей из системы.
    """
    next_page = reverse_lazy('landing')
    template_name = 'users/logout.html'  # Добавляем шаблон для страницы выхода
    
    def dispatch(self, request, *args, **kwargs):
        """
        Добавление сообщения перед выходом из системы.
        """
        if request.user.is_authenticated:
            messages.info(request, 'Вы успешно вышли из системы!')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    Представление (CBV) для профиля пользователя.
    Требует аутентификации пользователя.
    """
    template_name = 'users/profile.html'
    login_url = 'users:login'
    
    def get_context_data(self, **kwargs):
        """
        Добавление дополнительного контекста для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мой профиль'
        return context