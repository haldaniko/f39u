from __future__ import annotations

import os

from apps.news.models import Article, ArticleSlugRedirect, Tag
from apps.news.slug_utils import unique_article_slug
from django.utils import timezone
from django.utils.text import slugify

from .providers import get_ai_rewriter


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _min_source_content_chars() -> int:
    return _env_int("ARTICLE_MIN_SOURCE_CONTENT_CHARS", 300)


def _min_rewritten_body_chars() -> int:
    return _env_int("ARTICLE_MIN_REWRITTEN_BODY_CHARS", 700)


class RewriteService:
    def _mark_not_publishable(self, article: Article, status: str = Article.Status.PENDING_REVIEW) -> None:
        article.status = status
        article.published_at = None
        article.save(update_fields=["status", "published_at", "updated_at"])

    def _has_publishable_source(self, article: Article) -> bool:
        return len((article.original_content or "").strip()) >= _min_source_content_chars()

    def _has_publishable_result(self, result: dict[str, object]) -> bool:
        body = str(result.get("body") or "").strip()
        if str(result.get("_fallback", "")).lower() == "true":
            return False
        if len(body) < _min_rewritten_body_chars():
            return False
        if len(body.split()) < 120:
            return False
        if not str(result.get("title") or "").strip():
            return False
        if not str(result.get("summary") or "").strip():
            return False
        return True

    def rewrite_pending_articles(self, limit: int = 10) -> int:
        rewriter = get_ai_rewriter()
        rewritten = 0
        queryset = Article.objects.filter(status=Article.Status.DRAFT).order_by("created_at")[:limit]
        for article in queryset:
            if not self._has_publishable_source(article):
                self._mark_not_publishable(article, status=Article.Status.REJECTED)
                continue

            result = rewriter.rewrite({"title": article.original_title, "content": article.original_content})
            if not self._has_publishable_result(result):
                self._mark_not_publishable(article)
                continue

            article.rewritten_title = str(result["title"])
            article.rewritten_content = str(result["body"])
            article.summary = str(result["summary"])
            article.seo_description = str(result["seo_description"])
            article.title = article.rewritten_title
            new_slug = unique_article_slug(article.title, exclude_pk=article.pk)
            if article.slug != new_slug:
                ArticleSlugRedirect.objects.get_or_create(
                    old_slug=article.slug,
                    defaults={"article": article},
                )
                article.slug = new_slug
            article.status = Article.Status.PUBLISHED
            if not article.published_at:
                article.published_at = timezone.now()

            update_fields = [
                "rewritten_title",
                "rewritten_content",
                "summary",
                "seo_description",
                "title",
                "slug",
                "status",
                "published_at",
                "updated_at",
            ]
            article.save(update_fields=update_fields)
            for tag_name in result.get("tags", []):
                normalized_name = str(tag_name).strip()[:80]
                if not normalized_name:
                    continue
                tag_slug = slugify(normalized_name)[:100] or "tag"
                tag, _ = Tag.objects.get_or_create(
                    slug=tag_slug,
                    defaults={"name": normalized_name},
                )
                article.tags.add(tag)
            rewritten += 1
        return rewritten
