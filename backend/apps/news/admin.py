from django.contrib import admin

from .models import Article, Category, Source, Tag
from .services import NewsIngestionService


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source_name", "status", "published_at", "created_at")
    list_filter = ("status", "source_name", "category")
    search_fields = ("title", "original_title", "rewritten_title", "source_url")
    actions = ["approve_articles", "reject_articles"]

    @admin.action(description="Approve selected articles")
    def approve_articles(self, request, queryset):
        queryset.update(status=Article.Status.PUBLISHED)

    @admin.action(description="Reject selected articles")
    def reject_articles(self, request, queryset):
        queryset.update(status=Article.Status.REJECTED)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "enabled", "last_sync")
    list_filter = ("provider", "enabled")
    actions = ["run_sync_now"]

    @admin.action(description="Run source sync now")
    def run_sync_now(self, request, queryset):
        NewsIngestionService().fetch_and_store()
