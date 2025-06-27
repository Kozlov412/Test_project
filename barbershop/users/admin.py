from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Регистрируем модель Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'telegram_id', 'vk_id', 'created_at', 'updated_at') 
    search_fields = ('user__username', 'user__email', 'telegram_id', 'vk_id') 
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')