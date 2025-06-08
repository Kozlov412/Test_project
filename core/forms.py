from django import forms
from .models import Review, Master
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

class ReviewForm(forms.ModelForm):
    """
    Форма для создания нового отзыва
    """
    # Переопределяем поле master для лучшего стиля
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True),
        label="Мастер",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_master',
        }),
        empty_label="Выберите мастера"
    )
    
    # Переопределяем поле рейтинга, но скроем его в шаблоне и заменим на звездочки
    rating = forms.IntegerField(
        min_value=1, 
        max_value=5,
        label="Оценка",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'rating',
            'style': 'display: none;',  # Скрываем поле, использоваться будут звезды
        })
    )
    
    class Meta:
        model = Review
        fields = ['client_name', 'text', 'rating', 'master', 'photo']
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите ваш отзыв...',
                'rows': 4
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'client_name': 'Ваше имя',
            'text': 'Текст отзыва',
            'photo': 'Фотография (необязательно)',
        }
        help_texts = {
            'text': 'Поделитесь своими впечатлениями о нашем мастере',
            'photo': 'Вы можете приложить фотографию результата работы мастера',
        }

class UserLoginForm(AuthenticationForm):
    """
    Форма для входа пользователя в систему.
    Кастомизирует стандартную форму AuthenticationForm.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Настройка полей формы
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль',
        })
        
        # Русификация меток полей
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'


class UserRegisterForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей.
    Расширяет стандартную форму UserCreationForm, добавляя email.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email адрес',
        }),
        label='Email адрес',
    )
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
        # Переопределяем help_text для username
        help_texts = {
            'username': _('Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.')
        }
        # Русифицируем метки полей
        labels = {
            'username': 'Имя пользователя',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Настройка полей формы
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
        })
        
        # Русификация полей password1 и password2
        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = _(
            'Ваш пароль должен содержать не менее 8 символов, '
            'не должен быть слишком похож на другую вашу информацию, '
            'не должен быть часто используемым паролем и '
            'не должен состоять только из цифр.'
        )
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль',
        })
        
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password2'].help_text = _('Введите тот же пароль, что и выше, для проверки.')
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля',
        })
    
    def save(self, commit=True):
        """
        Переопределяем метод save для сохранения email.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user