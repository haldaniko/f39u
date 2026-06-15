from __future__ import annotations

from django.utils.text import slugify
from unidecode import unidecode


ARTICLE_SLUG_MAX_LENGTH = 280


def article_slug_base(title: str) -> str:
    transliterated = unidecode(str(title or ""))
    return slugify(transliterated)[:ARTICLE_SLUG_MAX_LENGTH] or "news-story"


def unique_article_slug(title: str, exclude_pk: int | None = None) -> str:
    from .models import Article, ArticleSlugRedirect

    base = article_slug_base(title)
    candidate = base
    counter = 2
    queryset = Article.objects.all()
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)

    while queryset.filter(slug=candidate).exists() or ArticleSlugRedirect.objects.filter(
        old_slug=candidate
    ).exists():
        suffix = f"-{counter}"
        candidate = f"{base[: ARTICLE_SLUG_MAX_LENGTH - len(suffix)]}{suffix}"
        counter += 1
    return candidate
