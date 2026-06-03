from __future__ import annotations

from celery import shared_task
from apps.ai.services import RewriteService

from .services import NewsCleanupService, NewsIngestionService


@shared_task
def fetch_latest_news_task() -> dict[str, int]:
    stats = NewsIngestionService().fetch_and_store()
    rewritten = RewriteService().rewrite_pending_articles(limit=50)
    stats["rewritten"] = rewritten
    return stats


@shared_task
def cleanup_duplicates_task() -> int:
    return NewsCleanupService.cleanup_duplicates()
