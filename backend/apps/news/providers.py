from __future__ import annotations

import html
import os
import re
import struct
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urljoin

import feedparser
import requests

try:
    import trafilatura
except ImportError:  # pragma: no cover
    trafilatura = None

from .repositories import ArticleRepository, NormalizedArticle


class NewsProvider(ABC):
    @abstractmethod
    def fetch_articles(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def normalize_data(self, raw_article: dict[str, Any]) -> NormalizedArticle:
        raise NotImplementedError

    @staticmethod
    def _env_int(name: str, default: int) -> int:
        raw = os.getenv(name)
        if not raw:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    @classmethod
    def _min_content_chars(cls) -> int:
        return cls._env_int("ARTICLE_MIN_SOURCE_CONTENT_CHARS", 300)

    @classmethod
    def _min_image_width(cls) -> int:
        return cls._env_int("ARTICLE_MIN_IMAGE_WIDTH", 800)

    @classmethod
    def _min_image_height(cls) -> int:
        return cls._env_int("ARTICLE_MIN_IMAGE_HEIGHT", 450)

    @classmethod
    def _has_required_content(cls, normalized: NormalizedArticle) -> bool:
        return len((normalized.content or "").strip()) >= cls._min_content_chars()

    @classmethod
    def _image_dimensions_from_url(cls, url: str) -> tuple[int | None, int | None]:
        value = (url or "").lower()
        match = re.search(r"/(\d{2,5})x(\d{2,5})(?:/|[._-])", value)
        if match:
            return int(match.group(1)), int(match.group(2))

        width_match = re.search(r"[?&](?:w|width)=(\d{2,5})\b", value)
        height_match = re.search(r"[?&](?:h|height)=(\d{2,5})\b", value)
        width = int(width_match.group(1)) if width_match else None
        height = int(height_match.group(1)) if height_match else None
        return width, height

    @staticmethod
    def _parse_image_dimensions(image_bytes: bytes) -> tuple[int | None, int | None]:
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n") and len(image_bytes) >= 24:
            return struct.unpack(">II", image_bytes[16:24])

        if image_bytes.startswith((b"GIF87a", b"GIF89a")) and len(image_bytes) >= 10:
            return struct.unpack("<HH", image_bytes[6:10])

        if image_bytes.startswith(b"\xff\xd8"):
            index = 2
            length = len(image_bytes)
            while index + 9 < length:
                if image_bytes[index] != 0xFF:
                    index += 1
                    continue
                marker = image_bytes[index + 1]
                index += 2
                if marker in {0xD8, 0xD9}:
                    continue
                if index + 2 > length:
                    break
                segment_length = int.from_bytes(image_bytes[index : index + 2], "big")
                if segment_length < 2:
                    break
                if marker in {
                    0xC0,
                    0xC1,
                    0xC2,
                    0xC3,
                    0xC5,
                    0xC6,
                    0xC7,
                    0xC9,
                    0xCA,
                    0xCB,
                    0xCD,
                    0xCE,
                    0xCF,
                } and index + 7 <= length:
                    height = int.from_bytes(image_bytes[index + 3 : index + 5], "big")
                    width = int.from_bytes(image_bytes[index + 5 : index + 7], "big")
                    return width, height
                index += segment_length

        if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP" and len(image_bytes) >= 30:
            chunk = image_bytes[12:16]
            if chunk == b"VP8X":
                width = 1 + int.from_bytes(image_bytes[24:27], "little")
                height = 1 + int.from_bytes(image_bytes[27:30], "little")
                return width, height

        return None, None

    @classmethod
    def _probe_image_dimensions(cls, url: str) -> tuple[int | None, int | None]:
        fetch_url = f"https:{url}" if url.startswith("//") else url
        try:
            response = requests.get(
                fetch_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FutureXclusiveBot/1.0; +https://localhost)",
                    "Range": "bytes=0-65535",
                },
                timeout=8,
                stream=True,
            )
            response.raise_for_status()
        except requests.RequestException:
            return None, None

        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            chunks.append(chunk)
            total += len(chunk)
            if total >= 65536:
                break
        return cls._parse_image_dimensions(b"".join(chunks))

    @classmethod
    def _is_usable_image_url(cls, image_url: str) -> bool:
        image_url = (image_url or "").strip()
        if not image_url:
            return False
        # Accept absolute HTTP(S) and protocol-relative image URLs only.
        if not (image_url.startswith("http://") or image_url.startswith("https://") or image_url.startswith("//")):
            return False

        width, height = cls._image_dimensions_from_url(image_url)
        if width is None or height is None:
            probed_width, probed_height = cls._probe_image_dimensions(image_url)
            width = width or probed_width
            height = height or probed_height

        if width is None or height is None:
            return False
        return width >= cls._min_image_width() and height >= cls._min_image_height()

    @classmethod
    def _has_required_image(cls, normalized: NormalizedArticle) -> bool:
        return cls._is_usable_image_url(normalized.image_url)

    def save_articles(self, raw_articles: list[dict[str, Any]]) -> int:
        changed = 0
        for item in raw_articles:
            normalized = self.normalize_data(item)
            if not self._has_required_content(normalized):
                continue
            if not self._has_required_image(normalized):
                continue
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
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "https://www.ft.com/rss/home",
        "https://www.forbes.com/business/feed/",
        "https://fortune.com/feed/",
        "https://venturebeat.com/feed",
        "https://news.crunchbase.com/feed/",
        "https://www.epravda.com.ua/rss/",
        "https://www.investor.bg/rss/latest",
        "https://www.dnes.bg/rss.php?cat=2",
    ]
    teaser_patterns = [
        r"\bread the full story\b.*$",
        r"\bread more\b.*$",
        r"\bcontinue reading\b.*$",
        r"\bfull article\b.*$",
        r"\bclick here\b.*$",
        r"\bvisit (the )?original\b.*$",
        r"\boriginally published at\b.*$",
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

    def _strip_teaser_phrases(self, text: str) -> str:
        value = (text or "").strip()
        if not value:
            return ""

        lines = [line.strip() for line in value.splitlines() if line.strip()]
        cleaned_lines: list[str] = []
        for line in lines:
            normalized = line
            for pattern in self.teaser_patterns:
                normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE).strip(" -:\u2014")
            if normalized:
                cleaned_lines.append(normalized)

        cleaned = "\n\n".join(cleaned_lines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned

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
                return self._strip_teaser_phrases(text)

        summary = str(entry.get("summary", ""))
        return self._strip_teaser_phrases(self._strip_html_tags(summary))

    def _fetch_full_article_text(self, url: str) -> str:
        if not url:
            return ""
        try:
            resp = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (compatible; FutureXclusiveBot/1.0; +https://localhost)"},
            )
            resp.raise_for_status()
        except requests.RequestException:
            return ""

        if trafilatura is not None:
            extracted = trafilatura.extract(
                resp.text,
                include_comments=False,
                include_formatting=False,
                favor_recall=True,
            )
            if extracted:
                return self._strip_teaser_phrases(extracted)

        return self._strip_teaser_phrases(self._extract_text_candidate_from_html(resp.text))

    def _fetch_image_from_article_page(self, url: str) -> str:
        if not url:
            return ""
        try:
            resp = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (compatible; FutureXclusiveBot/1.0; +https://localhost)"},
            )
            resp.raise_for_status()
        except requests.RequestException:
            return ""

        html_doc = resp.text or ""
        if not html_doc:
            return ""

        # Prefer metadata images because they are typically high quality and canonical.
        for pattern in (
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+itemprop=["\']image["\'][^>]+content=["\']([^"\']+)["\']',
        ):
            match = re.search(pattern, html_doc, flags=re.IGNORECASE)
            if match and match.group(1).strip():
                return urljoin(url, match.group(1).strip())

        first_image = self._extract_first_image_from_html(html_doc)
        return urljoin(url, first_image) if first_image else ""

    @staticmethod
    def _upgrade_image_url(url: str) -> str:
        upgraded = (url or "").strip()
        if not upgraded:
            return ""

        # BBC RSS frequently exposes tiny thumbnails; switch to larger known variants.
        upgraded = upgraded.replace("/ace/standard/240/", "/ace/standard/1024/")
        upgraded = upgraded.replace("/images/ic/240x135/", "/images/ic/1024x576/")
        # Investor.bg and Dnes.bg RSS expose 200x113 thumbnails while article metadata has 1280x720.
        upgraded = re.sub(r"(/media/files/resized/article/)200x113/", r"\g<1>1280x720/", upgraded)
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
        fulltext_budget_per_feed = int(os.getenv("RSS_FULLTEXT_FETCH_LIMIT_PER_FEED", "12"))
        image_fetch_budget_per_feed = int(os.getenv("RSS_IMAGE_FETCH_LIMIT_PER_FEED", "8"))
        for feed_url in self._get_feed_urls():
            fulltext_budget = fulltext_budget_per_feed
            image_fetch_budget = image_fetch_budget_per_feed
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
                content = self._strip_teaser_phrases(content)
                image = self._upgrade_image_url(self._extract_image(entry))
                if (not image or not self._is_usable_image_url(image)) and image_fetch_budget > 0:
                    page_image = self._upgrade_image_url(self._fetch_image_from_article_page(link))
                    if page_image:
                        image = page_image
                    image_fetch_budget -= 1
                collected.append(
                    {
                        "title": entry.get("title", "Untitled"),
                        "summary": content,
                        "source": feed_title,
                        "url": link,
                        "image": image,
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
