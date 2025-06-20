from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Миксин, который проверяет, является ли пользователь сотрудником.
    Используется для ограничения доступа к представлениям, предназначенным
    только для персонала (staff).
    """
    permission_denied_message = "Доступ запрещен. Необходимы права сотрудника."
    
    def test_func(self):
        """
        Проверка, является ли пользователь аутентифицированным и
        имеет ли статус staff.
        """
        return self.request.user.is_authenticated and self.request.user.is_staff
    
    def handle_no_permission(self):
        """
        Обработка случая, когда у пользователя нет прав доступа.
        Добавляет сообщение об ошибке и перенаправляет пользователя.
        """
        messages.error(self.request, self.permission_denied_message)
        return redirect('landing')


class SuperUserRequiredMixin(UserPassesTestMixin):
    """
    Миксин, который проверяет, является ли пользователь суперпользователем.
    Используется для ограничения доступа к особо важным административным функциям.
    """
    permission_denied_message = "Доступ запрещен. Требуются права администратора."
    
    def test_func(self):
        """
        Проверка, является ли пользователь аутентифицированным и
        имеет ли статус superuser.
        """
        return self.request.user.is_authenticated and self.request.user.is_superuser
    
    def handle_no_permission(self):
        """
        Обработка случая, когда у пользователя нет прав доступа.
        Добавляет сообщение об ошибке и перенаправляет пользователя.
        """
        messages.error(self.request, self.permission_denied_message)
        return redirect('landing')


class OwnerOrStaffRequiredMixin(UserPassesTestMixin):
    """
    Миксин, который проверяет, является ли пользователь владельцем объекта
    или сотрудником. Используется для обеспечения доступа пользователя к его
    собственным данным или администраторам ко всем данным.
    """
    permission_denied_message = "У вас нет прав доступа к этому ресурсу."
    owner_field = 'user'  # Поле, которое указывает на владельца объекта
    
    def test_func(self):
        """
        Проверяет, является ли пользователь владельцем объекта или сотрудником.
        Объект доступен через метод get_object(), который вызывается
        при обработке запроса в DetailView, UpdateView, DeleteView.
        """
        if not self.request.user.is_authenticated:
            return False
            
        # Для сотрудников доступ разрешен всегда
        if self.request.user.is_staff:
            return True
        
        # Получаем объект, если его еще нет
        if not hasattr(self, 'object'):
            self.object = self.get_object()
            
        # Проверяем, является ли пользователь владельцем
        owner = getattr(self.object, self.owner_field, None)
        return owner == self.request.user
    
    def handle_no_permission(self):
        """
        Обработка случая, когда у пользователя нет прав доступа.
        Добавляет сообщение об ошибке и перенаправляет пользователя.
        """
        messages.error(self.request, self.permission_denied_message)
        return redirect('landing')