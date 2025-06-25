from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserLoginView, UserLogoutView, UserRegisterView, UserProfileView

app_name = 'users'  # Пространство имен для URL-маршрутов

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Восстановление пароля (опционально)
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html',
            subject_template_name='users/password_reset_subject.txt',
            email_template_name='users/password_reset_email.html',
            success_url='/users/password-reset/done/',
        ), 
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url='/users/password-reset-complete/',
        ), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ), 
        name='password_reset_complete'),
    
    # Смена пароля (опционально)
    path('password-change/', 
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change.html',
            success_url='/users/password-change/done/',
        ), 
        name='password_change'),
    path('password-change/done/', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ), 
        name='password_change_done'),
]