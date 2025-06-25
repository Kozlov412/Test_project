from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Бэкенд аутентификации, позволяющий пользователям входить 
    как по имени пользователя, так и по email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Проверяем, существует ли пользователь с таким username или email
            user = User.objects.get(
                Q(username__iexact=username) | 
                Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None