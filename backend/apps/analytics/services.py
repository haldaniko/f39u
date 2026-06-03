from __future__ import annotations

from datetime import date

from django.db.models import Count

from apps.news.models import Article

from .models import DailyAnalyticsReport


class AnalyticsService:
    @staticmethod
    def build_statistics() -> dict[str, int]:
        by_source = Article.objects.values("source_name").annotate(total=Count("id")).order_by("-total")
        return {item["source_name"]: item["total"] for item in by_source}

    @staticmethod
    def create_daily_report() -> DailyAnalyticsReport:
        return DailyAnalyticsReport.objects.update_or_create(
            date=date.today(),
            defaults={
                "total_articles": Article.objects.count(),
                "published_articles": Article.objects.filter(status=Article.Status.PUBLISHED).count(),
                "pending_articles": Article.objects.filter(status=Article.Status.PENDING_REVIEW).count(),
                "source_statistics": AnalyticsService.build_statistics(),
            },
        )[0]
