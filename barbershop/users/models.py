from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('Аватар'), upload_to='users/avatars/', null=True, blank=True)
    birth_date = models.DateField(_('Дата рождения'), null=True, blank=True)
    telegram_id = models.CharField(
        _('ID Telegram'),
        max_length=32,
        blank=True,
        validators=[RegexValidator(
            regex=r'^@?[\w]{5,32}$',
            message='Введите корректный Telegram ID (от 5 до 32 символов, буквы, цифры, знак подчеркивания)'
        )]
    )
    vk_id = models.CharField(  
        _('ID ВКонтакте'),
        max_length=50,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_.]{5,50}$',
            message='Введите корректный ID ВКонтакте (от 5 до 50 символов: буквы, цифры, точка, подчеркивание)'
        )]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Профиль')
        verbose_name_plural = _('Профили')

    def __str__(self):
        return f"Профиль {self.user.username}"

    def get_absolute_url(self):
        return reverse('users:profile_detail', kwargs={'pk': self.pk})

