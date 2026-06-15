from __future__ import annotations

import json
import os
import re
from html import escape
from urllib.parse import urljoin

import requests
from django.http import Http404, HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Article, ArticleSlugRedirect, Author, Category
from .services import NewsQueryService

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
ROOT_ELEMENT_PATTERN = re.compile(
    r'(<div\s+id=["\']root["\'][^>]*>)\s*(</div>)',
    flags=re.IGNORECASE,
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


def _spa_shell(seo_head: str, root_html: str = "") -> HttpResponse:
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

    if root_html:
        html_with_content = ROOT_ELEMENT_PATTERN.sub(
            lambda match: f"{match.group(1)}{root_html}{match.group(2)}",
            html,
            count=1,
        )
        if html_with_content == html:
            return HttpResponse("Frontend root element is not configured.", status=503)
        html = html_with_content

    return HttpResponse(html, content_type="text/html; charset=utf-8")


def article_page(request: HttpRequest, slug: str) -> HttpResponse:
    queryset = (
        Article.objects.filter(status=Article.Status.PUBLISHED)
        .select_related("category", "author")
        .prefetch_related("tags")
    )
    article = queryset.filter(slug=slug).first()
    if article is None:
        redirect = (
            ArticleSlugRedirect.objects.select_related("article")
            .filter(old_slug=slug, article__status=Article.Status.PUBLISHED)
            .first()
        )
        if redirect is None:
            raise Http404("Article not found")
        return HttpResponsePermanentRedirect(f"/article/{redirect.article.slug}")
    publication_date = article.published_at or article.created_at
    published_at = publication_date.isoformat()
    updated_at = (article.updated_at or publication_date).isoformat()
    article_url = _absolute_url(f"/article/{article.slug}")
    author = article.author
    if author:
        author_url = _absolute_url(f"/author/{author.slug}")
        author_data = {
            "@type": "Person",
            "name": author.name,
            "url": author_url,
        }
        social_urls = [
            url
            for url in [author.x_url, author.linkedin_url, author.instagram_url]
            if url
        ]
        if social_urls:
            author_data["sameAs"] = social_urls
    else:
        author_data = {
            "@type": "Organization",
            "name": "Future Xclusive News",
            "url": _absolute_url("/"),
        }
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
        "author": author_data,
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

    body_content = article.rewritten_content or article.original_content
    body_paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n|\n", body_content)
        if paragraph.strip()
    ]
    root_html = render_to_string(
        "news/article_ssr.html",
        {
            "article": article,
            "publication_date": publication_date,
            "body_paragraphs": body_paragraphs,
            "tags": article.tags.all(),
            "related_articles": NewsQueryService.related(article, limit=4),
            "current_year": timezone.now().year,
        },
    )

    return _spa_shell(
        _seo_head(
            title=article.title,
            description=article.seo_description or article.summary,
            path=f"/article/{article.slug}",
            image=article.image_url,
            page_type="article",
            published_at=published_at,
            structured_data=structured_data,
        ),
        root_html=root_html,
    )


def author_page(request: HttpRequest, slug: str) -> HttpResponse:
    author = get_object_or_404(Author, slug=slug)
    articles = list(
        author.articles.filter(status=Article.Status.PUBLISHED)
        .select_related("category")
        .order_by("-published_at", "-created_at")[:50]
    )
    author_url = _absolute_url(f"/author/{author.slug}")
    social_urls = [
        url
        for url in [author.x_url, author.linkedin_url, author.instagram_url]
        if url
    ]
    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": author.name,
        "url": author_url,
        "jobTitle": author.job_title,
        "description": _clean_text(author.bio),
    }
    if author.photo_url:
        person_schema["image"] = _absolute_url(author.photo_url)
    if author.location:
        person_schema["homeLocation"] = {
            "@type": "Place",
            "name": author.location,
        }
    if social_urls:
        person_schema["sameAs"] = social_urls

    root_html = render_to_string(
        "news/author_ssr.html",
        {
            "author": author,
            "articles": articles,
            "current_year": timezone.now().year,
        },
    )
    return _spa_shell(
        _seo_head(
            title=f"{author.name}, {author.job_title}",
            description=author.bio,
            path=f"/author/{author.slug}",
            image=author.photo_url,
            structured_data=person_schema,
        ),
        root_html=root_html,
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
