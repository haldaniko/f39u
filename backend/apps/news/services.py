from __future__ import annotations

from collections import Counter

from django.db.models import Count

from .models import Article
from .providers import get_providers
from .repositories import ArticleRepository


class NewsIngestionService:
    def fetch_and_store(self) -> dict[str, int]:
        stats: dict[str, int] = {}
        for provider in get_providers():
            raw = provider.fetch_articles()
            stats[provider.__class__.__name__] = provider.save_articles(raw)
        return stats


class NewsQueryService:
    @staticmethod
    def trending(limit: int = 8):
        return ArticleRepository.published().annotate(tag_count=Count("tags")).order_by("-tag_count", "-published_at")[:limit]

    @staticmethod
    def popular_categories(limit: int = 6) -> list[dict[str, int | str]]:
        data = (
            ArticleRepository.published()
            .values("category__name")
            .annotate(total=Count("id"))
            .order_by("-total")[:limit]
        )
        return [{"name": item["category__name"] or "General", "total": item["total"]} for item in data]


class NewsCleanupService:
    @staticmethod
    def cleanup_duplicates() -> int:
        seen = Counter()
        deleted = 0
        for article in Article.objects.order_by("source_url", "id"):
            seen[article.source_url] += 1
            if seen[article.source_url] > 1:
                article.delete()
                deleted += 1
        return deleted
