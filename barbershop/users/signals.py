from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Создание или обновление профиля пользователя при создании/обновлении экземпляра User
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Обновление профиля при обновлении пользователя
        instance.profile.save()