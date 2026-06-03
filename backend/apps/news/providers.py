from __future__ import annotations

import html
import os
import re
from abc import ABC, abstractmethod
from typing import Any

import feedparser
import requests

from .repositories import ArticleRepository, NormalizedArticle


class NewsProvider(ABC):
    @abstractmethod
    def fetch_articles(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def normalize_data(self, raw_article: dict[str, Any]) -> NormalizedArticle:
        raise NotImplementedError

    def save_articles(self, raw_articles: list[dict[str, Any]]) -> int:
        changed = 0
        for item in raw_articles:
            normalized = self.normalize_data(item)
            _, was_changed = ArticleRepository.upsert_original(normalized)
            if was_changed:
                changed += 1
        return changed


class NewsApiProvider(NewsProvider):
    endpoint = "https://newsapi.org/v2/top-headlines"

    def fetch_articles(self) -> list[dict[str, Any]]:
        key = os.getenv("NEWSAPI_KEY", "")
        if not key:
            return []
        resp = requests.get(self.endpoint, params={"language": "en", "apiKey": key}, timeout=20)
        resp.raise_for_status()
        return resp.json().get("articles", [])

    def normalize_data(self, raw_article: dict[str, Any]) -> NormalizedArticle:
        return NormalizedArticle(
            title=raw_article.get("title", "Untitled"),
            content=raw_article.get("content") or raw_article.get("description") or "",
            source_name=raw_article.get("source", {}).get("name", "NewsAPI"),
            source_url=raw_article.get("url", ""),
            image_url=raw_article.get("urlToImage", ""),
            category="Top",
            tags=["breaking", "global"],
        )


class GNewsProvider(NewsProvider):
    endpoint = "https://gnews.io/api/v4/top-headlines"

    def fetch_articles(self) -> list[dict[str, Any]]:
        key = os.getenv("GNEWS_API_KEY", "")
        if not key:
            return []
        resp = requests.get(self.endpoint, params={"lang": "en", "token": key}, timeout=20)
        resp.raise_for_status()
        return resp.json().get("articles", [])

    def normalize_data(self, raw_article: dict[str, Any]) -> NormalizedArticle:
        return NormalizedArticle(
            title=raw_article.get("title", "Untitled"),
            content=raw_article.get("content") or raw_article.get("description") or "",
            source_name=raw_article.get("source", {}).get("name", "GNews"),
            source_url=raw_article.get("url", ""),
            image_url=raw_article.get("image", ""),
            category="Top",
            tags=["gnews"],
        )


class GuardianProvider(NewsProvider):
    endpoint = "https://content.guardianapis.com/search"

    def fetch_articles(self) -> list[dict[str, Any]]:
        key = os.getenv("GUARDIAN_API_KEY", "")
        if not key:
            return []
        resp = requests.get(
            self.endpoint,
            params={"api-key": key, "show-fields": "headline,bodyText,thumbnail"},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("response", {}).get("results", [])

    def normalize_data(self, raw_article: dict[str, Any]) -> NormalizedArticle:
        fields = raw_article.get("fields", {})
        return NormalizedArticle(
            title=fields.get("headline", raw_article.get("webTitle", "Untitled")),
            content=fields.get("bodyText", ""),
            source_name="The Guardian",
            source_url=raw_article.get("webUrl", ""),
            image_url=fields.get("thumbnail", ""),
            category=raw_article.get("sectionName", "World"),
            tags=["guardian"],
        )


class RSSProvider(NewsProvider):
    default_feeds = [
        "https://feeds.reuters.com/reuters/worldNews",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
    ]

    def _get_feed_urls(self) -> list[str]:
        configured = os.getenv("RSS_FEEDS", "").strip()
        if not configured:
            return self.default_feeds
        return [item.strip() for item in configured.split(",") if item.strip()]

    @staticmethod
    def _strip_html_tags(text: str) -> str:
        value = re.sub(r"<script.*?>.*?</script>", " ", text or "", flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r"<style.*?>.*?</style>", " ", value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r"<[^>]+>", " ", value)
        value = html.unescape(value)
        return re.sub(r"\s+", " ", value).strip()

    def _extract_text_candidate_from_html(self, page_html: str) -> str:
        if not page_html:
            return ""

        # Prefer article/main scoped blocks, then paragraphs fallback.
        scoped = re.findall(
            r"<(article|main)[^>]*>(.*?)</\1>",
            page_html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        scoped_html = " ".join(part for _, part in scoped)
        paragraph_source = scoped_html or page_html
        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", paragraph_source, flags=re.IGNORECASE | re.DOTALL)
        if not paragraphs:
            return ""

        joined = "\n\n".join(self._strip_html_tags(p) for p in paragraphs)
        cleaned = re.sub(r"\n{3,}", "\n\n", joined).strip()
        return cleaned

    def _extract_entry_content(self, entry: dict[str, Any]) -> str:
        blocks = entry.get("content") or []
        if blocks:
            combined = "\n\n".join(str(item.get("value", "")) for item in blocks if item.get("value"))
            text = self._strip_html_tags(combined)
            if text:
                return text

        summary = str(entry.get("summary", ""))
        return self._strip_html_tags(summary)

    def _fetch_full_article_text(self, url: str) -> str:
        if not url:
            return ""
        try:
            resp = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Facts39Bot/1.0; +https://localhost)"},
            )
            resp.raise_for_status()
        except requests.RequestException:
            return ""
        return self._extract_text_candidate_from_html(resp.text)

    @staticmethod
    def _upgrade_image_url(url: str) -> str:
        upgraded = (url or "").strip()
        if not upgraded:
            return ""

        # BBC RSS frequently exposes tiny thumbnails; switch to larger known variants.
        upgraded = upgraded.replace("/ace/standard/240/", "/ace/standard/1024/")
        upgraded = upgraded.replace("/images/ic/240x135/", "/images/ic/1024x576/")
        return upgraded

    @staticmethod
    def _extract_first_image_from_html(text: str) -> str:
        if not text:
            return ""
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_image(self, entry: dict[str, Any]) -> str:
        media_content = entry.get("media_content") or []
        for item in media_content:
            url = str(item.get("url", "")).strip()
            if url:
                return url

        media_thumbnail = entry.get("media_thumbnail") or []
        for item in media_thumbnail:
            url = str(item.get("url", "")).strip()
            if url:
                return url

        for link in entry.get("links", []) or []:
            rel = str(link.get("rel", "")).lower()
            mime_type = str(link.get("type", "")).lower()
            href = str(link.get("href", "")).strip()
            if href and (rel == "enclosure" or "image" in mime_type):
                return href

        image_meta = entry.get("image")
        if isinstance(image_meta, dict):
            url = str(image_meta.get("href") or image_meta.get("url") or "").strip()
            if url:
                return url

        image_url = str(entry.get("image_url", "")).strip()
        if image_url:
            return image_url

        summary = str(entry.get("summary", ""))
        return self._extract_first_image_from_html(summary)

    def fetch_articles(self) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        fulltext_budget = int(os.getenv("RSS_FULLTEXT_FETCH_LIMIT", "20"))
        for feed_url in self._get_feed_urls():
            parsed = feedparser.parse(feed_url)
            feed_title = parsed.feed.get("title", "RSS")
            for entry in parsed.entries[:30]:
                link = entry.get("link", "")
                if not link:
                    continue
                tags = [tag.get("term", "") for tag in entry.get("tags", []) if tag.get("term")]
                content = self._extract_entry_content(entry)
                if len(content) < 700 and fulltext_budget > 0:
                    full_text = self._fetch_full_article_text(link)
                    if len(full_text) > len(content):
                        content = full_text
                    fulltext_budget -= 1
                collected.append(
                    {
                        "title": entry.get("title", "Untitled"),
                        "summary": content,
                        "source": feed_title,
                        "url": link,
                        "image": self._extract_image(entry),
                        "category": tags[0] if tags else "RSS",
                        "tags": tags or ["rss"],
                    }
                )
        return collected

    def normalize_data(self, raw_article: dict[str, Any]) -> NormalizedArticle:
        return NormalizedArticle(
            title=raw_article.get("title", "Untitled"),
            content=raw_article.get("summary", ""),
            source_name=raw_article.get("source", "RSS"),
            source_url=raw_article.get("url", ""),
            image_url=self._upgrade_image_url(raw_article.get("image", "")),
            category=raw_article.get("category", "RSS"),
            tags=raw_article.get("tags", []),
        )


def get_providers() -> list[NewsProvider]:
    return [NewsApiProvider(), GNewsProvider(), GuardianProvider(), RSSProvider()]
