from __future__ import annotations

from celery import shared_task

from .services import NewsCleanupService, NewsIngestionService


@shared_task
def fetch_latest_news_task() -> dict[str, int]:
    return NewsIngestionService().fetch_and_store()


@shared_task
def cleanup_duplicates_task() -> int:
    return NewsCleanupService.cleanup_duplicates()
