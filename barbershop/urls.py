"""
URL configuration for barbershop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Добавляем новый маршрут для создания услуги:
    path('services/create/', views.service_create, name='service_create'),
    # URL для создания нового мастера
    path('masters/create/', views.master_edit, name='master_create'),
    # URL для редактирования существующего мастера
    path('masters/<int:master_id>/edit/', views.master_edit, name='master_edit'),
    # Подключаем urls приложения users с использованием namespace
    path('users/', include('users.urls', namespace='users')),
    # Другие маршруты
    path('', include('core.urls')),
    
]

# Для отображения медиа и статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()