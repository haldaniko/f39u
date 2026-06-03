from django.contrib import admin

from .models import AISetting


@admin.register(AISetting)
class AISettingAdmin(admin.ModelAdmin):
    list_display = ("provider", "model", "temperature", "max_tokens", "is_active", "updated_at")
    list_filter = ("provider", "is_active")
