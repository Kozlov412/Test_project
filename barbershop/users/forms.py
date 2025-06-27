from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm, 
    PasswordChangeForm,
    PasswordResetForm, 
    SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from .models import Profile

class UserLoginForm(AuthenticationForm):
    """Форма для входа в систему"""
    
    username = forms.CharField(
        label=_('Имя пользователя или Email'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите имя пользователя или email'),
            'autocomplete': 'username',
        })
    )
    
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите пароль'),
            'autocomplete': 'current-password',
        })
    )

class UserRegisterForm(UserCreationForm):
    """Форма для регистрации новых пользователей"""
    
    email = forms.EmailField(
        required=True,
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите email'),
            'autocomplete': 'email',
        })
    )
    
    username = forms.CharField(
        label=_('Имя пользователя'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите имя пользователя'),
            'autocomplete': 'username',
        }),
        help_text=None,
    )
    
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Придумайте пароль'),
            'autocomplete': 'new-password',
        }),
        help_text=None,
    )
    
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Повторите пароль'),
            'autocomplete': 'new-password',
        }),
        help_text=None,
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Пользователь с таким email уже существует'))
        return email

class UserProfileUpdateForm(forms.ModelForm):
    """Форма для обновления профиля пользователя"""
    
    username = forms.CharField(
        label=_('Имя пользователя'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    
    first_name = forms.CharField(
        label=_('Имя'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    last_name = forms.CharField(
        label=_('Фамилия'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проверка наличия профиля у пользователя
        try:
            self.profile = self.instance.profile
        except Profile.DoesNotExist:
            self.profile = Profile.objects.create(user=self.instance)

class ProfileUpdateForm(forms.ModelForm):
    """Форма для обновления дополнительных данных профиля"""
    
    birth_date = forms.DateField(
        label=_('Дата рождения'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
    )
    
    telegram_id = forms.CharField(
        label=_('Telegram ID'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('@username'),
        }),
    )
    
    vk_id = forms.CharField(  # Заменяем github_id на vk_id
        label=_('ID ВКонтакте'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('username'),
        }),
    )
    
    avatar = forms.ImageField(
        label=_('Аватар'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
    )
    
    class Meta:
        model = Profile
        fields = ['avatar', 'birth_date', 'telegram_id', 'vk_id']

class UserPasswordChangeForm(PasswordChangeForm):
    """Форма для изменения пароля пользователя"""
    
    old_password = forms.CharField(
        label=_('Текущий пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите текущий пароль'),
            'autocomplete': 'current-password',
        }),
        help_text=None,
    )
    
    new_password1 = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите новый пароль'),
            'autocomplete': 'new-password',
        }),
        help_text=None,
    )
    
    new_password2 = forms.CharField(
        label=_('Подтверждение нового пароля'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Повторите новый пароль'),
            'autocomplete': 'new-password',
        }),
        help_text=None,
    )

class CustomPasswordResetForm(PasswordResetForm):
    """Форма для запроса на сброс пароля"""
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите ваш email'),
            'autocomplete': 'email',
        }),
    )

class CustomSetPasswordForm(SetPasswordForm):
    """Форма для установки нового пароля при сбросе"""
    
    new_password1 = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Введите новый пароль'),
            'autocomplete': 'new-password',
        }),
        help_text=None,
    )
    
    new_password2 = forms.CharField(
        label=_('Подтверждение нового пароля'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Повторите новый пароль'),
            'autocomplete': 'new-password',
        }),
        help_text=None,
    )