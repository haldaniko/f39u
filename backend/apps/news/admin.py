from django.contrib import admin

from .models import Article, ArticleSlugRedirect, Author, Category, NewsletterSubscriber, Source, Tag
from .services import NewsIngestionService


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "source_name", "status", "published_at", "created_at")
    list_filter = ("status", "source_name", "categories", "author")
    filter_horizontal = ("categories", "tags")
    search_fields = ("title", "original_title", "rewritten_title", "source_url")
    actions = ["approve_articles", "reject_articles"]

    @admin.action(description="Approve selected articles")
    def approve_articles(self, request, queryset):
        for article in queryset.select_related("category").prefetch_related("categories"):
            if not article.category_id and not article.categories.exists():
                continue
            article.status = Article.Status.PUBLISHED
            article.save(update_fields=["status", "updated_at"])

    @admin.action(description="Reject selected articles")
    def reject_articles(self, request, queryset):
        queryset.update(status=Article.Status.REJECTED)


@admin.register(ArticleSlugRedirect)
class ArticleSlugRedirectAdmin(admin.ModelAdmin):
    list_display = ("old_slug", "article", "created_at")
    search_fields = ("old_slug", "article__title", "article__slug")
    readonly_fields = ("old_slug", "article", "created_at")


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "job_title", "location", "joined_at")
    search_fields = ("name", "job_title", "bio")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "source", "is_active", "subscribed_at")
    list_filter = ("source", "is_active")
    search_fields = ("email",)
    readonly_fields = ("email", "source", "subscribed_at", "updated_at")


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
