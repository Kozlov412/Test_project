from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, UserRegisterView, 
    UserProfileDetailView, UserProfileUpdateView,
    UserPasswordChangeView, CustomPasswordResetView,
    CustomPasswordResetDoneView, CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

app_name = 'users'

urlpatterns = [
    # Регистрация, вход и выход
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Профиль пользователя
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='profile_edit'),
    
    # Смена пароля
    path('password_change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', UserPasswordChangeView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
    
    # Восстановление пароля
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('password-reset-complete/', CustomPasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
]