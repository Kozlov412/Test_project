from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, 
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import (
    UserLoginForm, UserRegisterForm, UserProfileUpdateForm, 
    ProfileUpdateForm, UserPasswordChangeForm,
    CustomPasswordResetForm, CustomSetPasswordForm
)
from .models import Profile

User = get_user_model()

class UserRegisterView(CreateView):
    """Представление для регистрации новых пользователей"""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('landing')  # URL для перенаправления после успешной регистрации
    
    def dispatch(self, request, *args, **kwargs):
        """Перенаправление аутентифицированных пользователей"""
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
        response = super().form_valid(form)
        user = form.save()
        # Явно указываем бэкенд для избежания проблем с множественными бэкендами
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        # Автоматический вход после регистрации
        login(self.request, user)
        # Добавление сообщения об успешной регистрации
        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать!')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Обработка невалидной формы с добавлением сообщения об ошибке
        """
        messages.error(self.request, 'Ошибка регистрации. Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class UserLoginView(LoginView):
    """Представление для входа пользователей в систему"""
    template_name = 'users/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    
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
        """Обработка невалидной формы с добавлением сообщения об ошибке"""
        messages.error(self.request, 'Ошибка входа. Пожалуйста, проверьте имя пользователя и пароль.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в аккаунт'
        return context


class UserLogoutView(LogoutView):
    """Представление для выхода пользователей из системы"""
    next_page = reverse_lazy('landing')
    
    def dispatch(self, request, *args, **kwargs):
        """Добавление сообщения перед выходом из системы"""
        if request.user.is_authenticated:
            messages.info(request, 'Вы успешно вышли из системы!')
        return super().dispatch(request, *args, **kwargs)


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """Представление для отображения профиля пользователя"""
    model = Profile
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile'
    
    def get_object(self, queryset=None):
        """Получение объекта профиля, обеспечивая его существование"""
        obj = get_object_or_404(Profile, pk=self.kwargs.get('pk'))
        return obj
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Профиль пользователя {self.object.user.username}'
        context['is_owner'] = self.request.user == self.object.user
        return context


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Представление для обновления профиля пользователя"""
    model = Profile  # Добавьте модель
    template_name = 'users/profile_update_form.html'
    # Добавьте одно из следующих:
    form_class = ProfileUpdateForm  # Вариант 1: предпочтительно, если у вас есть кастомная форма
    # или 
    # fields = ['avatar', 'birth_date', 'telegram_id', 'vk_id']  # Вариант 2: если нет кастомной формы
    
    def test_func(self):
        """Проверка, что пользователь редактирует свой профиль"""
        return self.request.user.profile == self.get_object()
    
    def get_object(self, queryset=None):
        """Получить профиль текущего пользователя"""
        return self.request.user.profile
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
        
        if 'user_form' not in context:
            context['user_form'] = UserProfileUpdateForm(instance=self.request.user)
        if 'profile_form' not in context:
            context['profile_form'] = ProfileUpdateForm(instance=self.get_object())
            
        return context
    
    def form_invalid(self, **kwargs):
        """Обработка невалидной формы"""
        return self.render_to_response(self.get_context_data(**kwargs))
    
    def get_success_url(self):
        """URL для перенаправления после успешного обновления"""
        messages.success(self.request, 'Профиль успешно обновлен!')
        return reverse_lazy('users:profile_detail', kwargs={'pk': self.object.pk})
    
    def post(self, request, *args, **kwargs):
        """Обработка POST запроса с двумя формами"""
        self.object = self.get_object()
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=self.object)
        
        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        else:
            return self.form_invalid(user_form=user_form, profile_form=profile_form)
    
    def form_valid(self, user_form, profile_form):
        """Сохранение форм при успешной валидации"""
        with transaction.atomic():
            user_form.save()
            profile_form.save()
        return redirect(self.get_success_url())


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Представление для изменения пароля пользователя"""
    template_name = 'users/password_change_form.html'
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    
    def form_valid(self, form):
        """Обработка валидной формы"""
        messages.success(self.request, 'Ваш пароль был изменен!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение пароля'
        return context


class CustomPasswordResetView(PasswordResetView):
    """Представление для запроса на сброс пароля"""
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        return context


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Представление страницы успешной отправки инструкций по сбросу пароля"""
    template_name = 'users/password_reset_done.html'
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Инструкции по сбросу пароля отправлены'
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Представление страницы установки нового пароля"""
    template_name = 'users/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установка нового пароля'
        return context


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Представление страницы успешной установки нового пароля"""
    template_name = 'users/password_reset_complete.html'
    
    def get_context_data(self, **kwargs):
        """Добавление дополнительного контекста для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пароль успешно изменен'
        return context