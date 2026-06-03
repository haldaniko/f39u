from django.contrib import admin

from .models import DailyAnalyticsReport


@admin.register(DailyAnalyticsReport)
class DailyAnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ("date", "total_articles", "published_articles", "pending_articles", "created_at")
    readonly_fields = ("created_at",)
