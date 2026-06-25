from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.news.models import Article
from apps.news.providers import NewsProvider, RSSProvider


def _contains_cyrillic(text: str) -> bool:
    return any("\u0400" <= char <= "\u04ff" for char in text or "")


class Command(BaseCommand):
    help = "Repair or unpublish live articles that do not meet content and image quality gates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        extractor = RSSProvider()
        checked = repaired = unpublished = 0

        queryset = Article.objects.filter(status=Article.Status.PUBLISHED).order_by("id")
        for article in queryset.iterator():
            checked += 1
            update_fields: list[str] = []
            needs_rewrite = False

            has_source = len((article.original_content or "").strip()) >= NewsProvider._min_content_chars()
            if not has_source:
                full_text = extractor._fetch_full_article_text(article.source_url)
                if len(full_text.strip()) >= NewsProvider._min_content_chars():
                    article.original_content = full_text.strip()
                    article.rewritten_content = ""
                    update_fields.extend(["original_content", "rewritten_content"])
                    needs_rewrite = True

            if not NewsProvider._is_usable_image_url(article.image_url):
                candidate = extractor._upgrade_image_url(extractor._fetch_image_from_article_page(article.source_url))
                if candidate and NewsProvider._is_usable_image_url(candidate):
                    article.image_url = candidate
                    update_fields.append("image_url")

            has_source = len((article.original_content or "").strip()) >= NewsProvider._min_content_chars()
            has_image = NewsProvider._is_usable_image_url(article.image_url)
            has_body = len((article.rewritten_content or article.original_content or "").strip()) >= NewsProvider._min_content_chars()
            if _contains_cyrillic(article.rewritten_content):
                article.rewritten_content = ""
                update_fields.append("rewritten_content")
                needs_rewrite = True

            if has_source and has_image and has_body:
                if needs_rewrite:
                    article.status = Article.Status.DRAFT
                    article.published_at = None
                    update_fields.extend(["status", "published_at"])
                if update_fields:
                    repaired += 1
                    if not dry_run:
                        article.save(update_fields=sorted(set(update_fields + ["updated_at"])))
                continue

            unpublished += 1
            if not dry_run:
                article.status = Article.Status.REJECTED
                article.published_at = None
                article.save(update_fields=["status", "published_at", "updated_at"])

        action = "Would inspect" if dry_run else "Inspected"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {checked} published articles. "
                f"Repaired {repaired}; unpublished {unpublished}."
            )
        )
