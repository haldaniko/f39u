from __future__ import annotations

from apps.news.models import Article, Tag
from django.utils import timezone
from django.utils.text import slugify

from .providers import get_ai_rewriter


class RewriteService:
    def rewrite_pending_articles(self, limit: int = 10) -> int:
        rewriter = get_ai_rewriter()
        rewritten = 0
        queryset = Article.objects.filter(status=Article.Status.DRAFT).order_by("created_at")[:limit]
        for article in queryset:
            result = rewriter.rewrite({"title": article.original_title, "content": article.original_content})
            article.rewritten_title = str(result["title"])
            article.rewritten_content = str(result["body"])
            article.summary = str(result["summary"])
            article.seo_description = str(result["seo_description"])
            article.title = article.rewritten_title
            article.status = Article.Status.PUBLISHED
            if not article.published_at:
                article.published_at = timezone.now()

            update_fields = [
                "rewritten_title",
                "rewritten_content",
                "summary",
                "seo_description",
                "title",
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
