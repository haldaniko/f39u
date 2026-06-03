from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.news.services import NewsIngestionService


class Command(BaseCommand):
    help = "Fetch latest news from external providers and save them as draft articles for AI rewrite."

    def handle(self, *args, **options):
        stats = NewsIngestionService().fetch_and_store()
        total = sum(stats.values())
        self.stdout.write(self.style.SUCCESS(f"Fetched {total} external articles."))
        for provider, count in stats.items():
            self.stdout.write(f"- {provider}: {count}")