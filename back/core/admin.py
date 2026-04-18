# # Register your models here.
from django.contrib import admin
from .models import CustomUser  # Импортируем модель пользователя

# Вариант 1: Простая регистрация (выведет просто список)
# admin.site.register(CustomUser)

# Вариант 2: Красивая регистрация 
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Указываем, какие колонки показывать в таблице админки
    list_display = ('id', 'email', 'name', 'is_staff', 'is_active') 
    # Добавляем поиск по email и имени
    search_fields = ('email', 'name')