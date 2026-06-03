from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1

from django.db.models import QuerySet
from django.utils import timezone
from django.utils.text import slugify

from .models import Article, Category, Source, Tag


@dataclass
class NormalizedArticle:
    title: str
    content: str
    source_name: str
    source_url: str
    image_url: str = ""
    category: str = "General"
    tags: list[str] | None = None


class ArticleRepository:
    @staticmethod
    def _build_summary(content: str, title: str) -> str:
        normalized = " ".join(str(content).split())
        if normalized:
            return f"{normalized[:217]}..." if len(normalized) > 220 else normalized
        return title

    @staticmethod
    def _is_low_res_image(url: str) -> bool:
        value = (url or "").strip().lower()
        if not value:
            return True
        return any(marker in value for marker in ["/ace/standard/240/", "/images/ic/240x135/"])

    @staticmethod
    def _should_replace_image(existing_url: str, incoming_url: str) -> bool:
        incoming = (incoming_url or "").strip()
        existing = (existing_url or "").strip()
        if not incoming:
            return False
        if not existing:
            return True
        if incoming == existing:
            return False
        return ArticleRepository._is_low_res_image(existing) and not ArticleRepository._is_low_res_image(incoming)

    @staticmethod
    def _should_replace_content(existing_content: str, incoming_content: str) -> bool:
        incoming = (incoming_content or "").strip()
        existing = (existing_content or "").strip()
        if not incoming:
            return False
        if not existing:
            return True
        return len(incoming) >= len(existing) + 200

    @staticmethod
    def published() -> QuerySet[Article]:
        return Article.objects.filter(status=Article.Status.PUBLISHED)

    @staticmethod
    def pending_rewrite() -> QuerySet[Article]:
        return Article.objects.filter(status=Article.Status.DRAFT)

    @staticmethod
    def pending_review() -> QuerySet[Article]:
        return Article.objects.filter(status=Article.Status.PENDING_REVIEW)

    @staticmethod
    def get_by_slug(slug: str) -> Article:
        return Article.objects.get(slug=slug)

    @staticmethod
    def upsert_original(payload: NormalizedArticle) -> tuple[Article, bool]:
        category, _ = Category.objects.get_or_create(name=payload.category)
        base_slug = slugify(payload.title)[:240] or "article"
        unique_suffix = sha1(payload.source_url.encode("utf-8")).hexdigest()[:10]
        unique_slug = f"{base_slug}-{unique_suffix}"[:300]
        summary = ArticleRepository._build_summary(payload.content, payload.title)
        article, created = Article.objects.get_or_create(
            source_url=payload.source_url,
            defaults={
                "title": payload.title,
                "slug": unique_slug,
                "original_title": payload.title,
                "original_content": payload.content,
                "rewritten_title": payload.title,
                "rewritten_content": payload.content,
                "summary": summary,
                "seo_description": summary[:320],
                "source_name": payload.source_name,
                "image_url": payload.image_url,
                "category": category,
                "status": Article.Status.PUBLISHED,
                "published_at": timezone.now(),
            },
        )
        updated_fields: list[str] = []
        if not created:
            if ArticleRepository._should_replace_image(article.image_url, payload.image_url):
                article.image_url = payload.image_url
                updated_fields.append("image_url")
            if ArticleRepository._should_replace_content(article.original_content, payload.content):
                previous_original_content = article.original_content
                article.original_content = payload.content
                updated_fields.append("original_content")
                if article.rewritten_content == previous_original_content:
                    article.rewritten_content = payload.content
                    updated_fields.append("rewritten_content")
            if summary and (not article.summary or len(summary) > len(article.summary) + 40):
                article.summary = summary
                article.seo_description = summary[:320]
                updated_fields.extend(["summary", "seo_description"])
            if article.status != Article.Status.PUBLISHED:
                article.status = Article.Status.PUBLISHED
                updated_fields.append("status")
            if updated_fields:
                article.save(update_fields=updated_fields + ["updated_at"])

        if payload.tags:
            for tag_name in payload.tags:
                normalized_name = str(tag_name).strip()[:80]
                if not normalized_name:
                    continue
                tag_slug = slugify(normalized_name)[:100] or "tag"
                tag, _ = Tag.objects.get_or_create(
                    slug=tag_slug,
                    defaults={"name": normalized_name},
                )
                article.tags.add(tag)
        return article, (created or bool(updated_fields))


class SourceRepository:
    @staticmethod
    def enabled() -> QuerySet[Source]:
        return Source.objects.filter(enabled=True)
