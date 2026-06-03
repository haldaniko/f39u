from celery import shared_task

from .services import RewriteService


@shared_task
def rewrite_pending_articles_task() -> int:
    return RewriteService().rewrite_pending_articles(limit=20)
