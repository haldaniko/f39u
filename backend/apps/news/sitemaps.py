from __future__ import annotations

import os
from types import SimpleNamespace
from urllib.parse import urlparse

from django.contrib.sitemaps import Sitemap

from .models import Article, Category

SITE_URL = os.getenv("SITE_URL", "https://fxlfm.com").rstrip("/")
PARSED_SITE_URL = urlparse(SITE_URL)
CANONICAL_SITE = SimpleNamespace(domain=PARSED_SITE_URL.netloc)


class CanonicalSitemap(Sitemap):
    protocol = PARSED_SITE_URL.scheme or "https"

    def get_urls(self, page=1, site=None, protocol=None):
        return super().get_urls(
            page=page,
            site=CANONICAL_SITE,
            protocol=self.protocol,
        )


class ArticleSitemap(CanonicalSitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.filter(status=Article.Status.PUBLISHED).only(
            "slug",
            "updated_at",
        )

    def location(self, article: Article) -> str:
        return f"/article/{article.slug}"

    def lastmod(self, article: Article):
        return article.updated_at


class CategorySitemap(CanonicalSitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return (
            Category.objects.filter(articles__status=Article.Status.PUBLISHED)
            .distinct()
            .order_by("slug")
        )

    def location(self, category: Category) -> str:
        return f"/category/{category.slug}"


class StaticPageSitemap(CanonicalSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ["/", "/about", "/contact"]

    def location(self, path: str) -> str:
        return path


sitemaps = {
    "articles": ArticleSitemap,
    "categories": CategorySitemap,
    "static": StaticPageSitemap,
}
