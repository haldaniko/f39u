from __future__ import annotations

import json
import os
import re
from html import escape
from urllib.parse import urljoin

import requests
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from .models import Article, Category

SITE_NAME = "FXLFM"
SITE_URL = os.getenv("SITE_URL", "https://fxlfm.com").rstrip("/")
FRONTEND_INTERNAL_URL = os.getenv("FRONTEND_INTERNAL_URL", "http://frontend:4173").rstrip("/")
SEO_START = '<meta name="seo-head-start" content="">'
SEO_END = '<meta name="seo-head-end" content="">'
SEO_BLOCK_PATTERN = re.compile(
    r'<meta\s+name=["\']seo-head-start["\'][^>]*>.*?'
    r'<meta\s+name=["\']seo-head-end["\'][^>]*>',
    flags=re.DOTALL | re.IGNORECASE,
)


def _clean_text(value: str | None) -> str:
    return " ".join(re.sub(r"<[^>]*>", " ", value or "").split())


def _truncate(value: str | None, max_length: int) -> str:
    text = _clean_text(value)
    if len(text) <= max_length:
        return text

    shortened = text[: max_length - 3]
    last_space = shortened.rfind(" ")
    if last_space > max_length * 0.7:
        shortened = shortened[:last_space]
    return f"{shortened.strip()}..."


def _title(value: str) -> str:
    suffix = f" | {SITE_NAME}"
    clean_value = _clean_text(value)
    if clean_value.endswith(suffix):
        clean_value = clean_value[: -len(suffix)]
    return f"{_truncate(clean_value, 70 - len(suffix))}{suffix}"


def _absolute_url(value: str | None) -> str:
    return urljoin(f"{SITE_URL}/", value or "")


def _json_ld(data: dict[str, object]) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return payload.replace("<", "\\u003c")


def _seo_head(
    *,
    title: str,
    description: str,
    path: str,
    image: str = "",
    page_type: str = "website",
    published_at: str = "",
    structured_data: dict[str, object] | None = None,
    noindex: bool = False,
) -> str:
    page_title = _title(title)
    page_description = _truncate(
        description or "Read the latest global news, reporting and analysis from FXLFM.",
        160,
    )
    canonical_url = _absolute_url(path)
    image_url = _absolute_url(image) if image else ""
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    twitter_card = "summary_large_image" if image_url else "summary"

    tags = [
        SEO_START,
        f'<meta name="description" content="{escape(page_description, quote=True)}">',
        f'<meta name="robots" content="{robots}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:type" content="{page_type}">',
        f'<meta property="og:title" content="{escape(page_title, quote=True)}">',
        f'<meta property="og:description" content="{escape(page_description, quote=True)}">',
        f'<meta property="og:url" content="{escape(canonical_url, quote=True)}">',
        f'<meta name="twitter:card" content="{twitter_card}">',
        f'<meta name="twitter:title" content="{escape(page_title, quote=True)}">',
        f'<meta name="twitter:description" content="{escape(page_description, quote=True)}">',
        f'<link rel="canonical" href="{escape(canonical_url, quote=True)}">',
        f"<title>{escape(page_title)}</title>",
    ]

    if image_url:
        safe_image_url = escape(image_url, quote=True)
        tags.extend(
            [
                f'<meta property="og:image" content="{safe_image_url}">',
                f'<meta name="twitter:image" content="{safe_image_url}">',
            ]
        )
    if page_type == "article" and published_at:
        tags.append(
            f'<meta property="article:published_time" content="{escape(published_at, quote=True)}">'
        )
    if structured_data:
        tags.append(
            '<script type="application/ld+json" data-seo-structured-data="true">'
            f"{_json_ld(structured_data)}</script>"
        )

    tags.append(SEO_END)
    return "\n    ".join(tags)


def _spa_shell(seo_head: str) -> HttpResponse:
    try:
        response = requests.get(
            f"{FRONTEND_INTERNAL_URL}/",
            headers={"Host": "fxlfm.com"},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return HttpResponse("Frontend is temporarily unavailable.", status=503)

    html = SEO_BLOCK_PATTERN.sub(seo_head, response.text, count=1)
    if html == response.text:
        return HttpResponse("Frontend SEO shell is not configured.", status=503)
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def article_page(request: HttpRequest, slug: str) -> HttpResponse:
    article = get_object_or_404(
        Article.objects.filter(status=Article.Status.PUBLISHED)
        .select_related("category")
        .prefetch_related("tags"),
        slug=slug,
    )
    publication_date = article.published_at or article.created_at
    published_at = publication_date.isoformat()
    updated_at = (article.updated_at or publication_date).isoformat()
    article_url = _absolute_url(f"/article/{article.slug}")
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.title,
        "description": _clean_text(article.seo_description or article.summary or article.title),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": article_url,
        },
        "datePublished": published_at,
        "dateModified": updated_at,
        "author": {
            "@type": "Organization",
            "name": "Future Xclusive News",
            "url": _absolute_url("/"),
        },
        "publisher": {
            "@type": "Organization",
            "name": "Future Xclusive News",
            "url": _absolute_url("/"),
        },
    }
    if article.image_url:
        structured_data["image"] = [_absolute_url(article.image_url)]
    if article.category:
        structured_data["articleSection"] = article.category.name
    keywords = [tag.name for tag in article.tags.all()]
    if keywords:
        structured_data["keywords"] = ", ".join(keywords)

    return _spa_shell(
        _seo_head(
            title=article.title,
            description=article.seo_description or article.summary,
            path=f"/article/{article.slug}",
            image=article.image_url,
            page_type="article",
            published_at=published_at,
            structured_data=structured_data,
        )
    )


def category_page(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug)
    description = category.description or (
        f"Latest {category.name} news, stories and developments curated by FXLFM."
    )
    return _spa_shell(
        _seo_head(
            title=f"{category.name} News",
            description=description,
            path=f"/category/{category.slug}",
        )
    )


def about_page(request: HttpRequest) -> HttpResponse:
    return _spa_shell(
        _seo_head(
            title="About Us",
            description=(
                "Learn about FXLFM, an independent newsroom platform delivering timely "
                "global coverage with clear and transparent reporting."
            ),
            path="/about",
        )
    )


def contact_page(request: HttpRequest) -> HttpResponse:
    return _spa_shell(
        _seo_head(
            title="Contact the Editorial Team",
            description=(
                "Contact the FXLFM editorial team about corrections, partnerships, "
                "story tips or source information."
            ),
            path="/contact",
        )
    )


def search_page(request: HttpRequest) -> HttpResponse:
    return _spa_shell(
        _seo_head(
            title="Search News",
            description="Search FXLFM for the latest global news, reporting and analysis.",
            path="/search",
            noindex=True,
        )
    )
