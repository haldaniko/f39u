import json
import re
from unittest.mock import Mock, patch
from xml.etree import ElementTree

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .models import Article, Author, Category, Tag
from .seo_views import SEO_BLOCK_PATTERN, _seo_head


class SeoHeadTests(SimpleTestCase):
    def test_replaces_vite_seo_block_and_escapes_article_metadata(self):
        index_html = """
            <head>
              <meta name="seo-head-start" content="" />
              <title>Default title</title>
              <meta name="seo-head-end" content="" />
            </head>
        """
        seo_head = _seo_head(
            title='Markets & "Technology"',
            description='News about <strong>markets</strong> & technology.',
            path="/article/markets-technology",
            image="https://images.example.com/story.jpg",
            page_type="article",
            published_at="2026-06-15T12:00:00+00:00",
            structured_data={
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "headline": 'Markets & "Technology"',
                "datePublished": "2026-06-15T12:00:00+00:00",
                "author": {
                    "@type": "Organization",
                    "name": "Future Xclusive News",
                },
            },
        )

        rendered = SEO_BLOCK_PATTERN.sub(seo_head, index_html, count=1)

        self.assertNotIn("Default title", rendered)
        self.assertIn("Markets &amp; &quot;Technology&quot; | FXLFM", rendered)
        self.assertIn("News about markets &amp; technology.", rendered)
        self.assertIn('property="og:type" content="article"', rendered)
        self.assertIn('property="article:published_time"', rendered)
        self.assertIn('rel="canonical" href="https://fxlfm.com/article/markets-technology"', rendered)
        schema_match = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            rendered,
        )
        self.assertIsNotNone(schema_match)
        schema = json.loads(schema_match.group(1))
        self.assertEqual(schema["@type"], "NewsArticle")
        self.assertEqual(schema["headline"], 'Markets & "Technology"')
        self.assertEqual(schema["datePublished"], "2026-06-15T12:00:00+00:00")
        self.assertEqual(schema["author"]["name"], "Future Xclusive News")

    def test_long_title_keeps_brand_suffix(self):
        seo_head = _seo_head(
            title="A very long article headline " * 8,
            description="Description",
            path="/article/long-title",
        )

        self.assertIn("... | FXLFM</title>", seo_head)


class ArticleModelTests(TestCase):
    def test_slug_generated(self):
        category = Category.objects.create(name="Technology")
        article = Article.objects.create(
            title="AI Update",
            original_title="AI Update",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/1",
            category=category,
        )
        self.assertTrue(article.slug)

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class ArticleSchemaViewTests(TestCase):
    @patch("apps.news.seo_views.requests.get")
    def test_article_html_contains_complete_news_article_schema(self, mock_get):
        frontend_response = Mock()
        frontend_response.text = """
            <html><head>
              <meta name="seo-head-start" content="" />
              <title>Default title</title>
              <meta name="seo-head-end" content="" />
            </head><body><div id="root"></div></body></html>
        """
        frontend_response.raise_for_status.return_value = None
        mock_get.return_value = frontend_response

        category = Category.objects.create(name="Technology")
        tag = Tag.objects.create(name="Artificial Intelligence")
        author, _ = Author.objects.update_or_create(
            slug="maria-nicholson",
            defaults={
                "name": "Maria Nicholson",
                "job_title": "Senior News Editor",
                "bio": "Maria Nicholson covers global affairs, technology and business.",
                "photo_url": "https://images.example.com/maria.jpg",
                "location": "London, United Kingdom",
                "x_url": "https://x.com/marianicholsonnews",
                "linkedin_url": "https://www.linkedin.com/in/maria-nicholson-news/",
                "instagram_url": "https://www.instagram.com/marianicholson.news/",
                "joined_at": "2024-03-18",
            },
        )
        published_at = timezone.now()
        article = Article.objects.create(
            title="AI Changes the Technology Industry",
            original_title="AI Changes the Technology Industry",
            original_content="Original content",
            rewritten_content="First server-rendered paragraph.\n\nSecond paragraph with <script>alert('x')</script>.",
            summary="A detailed report about changes in the technology industry.",
            seo_description="How AI is changing the technology industry.",
            source_name="Unit Test",
            source_url="https://example.com/news/schema-test",
            image_url="https://images.example.com/ai-news.jpg",
            category=category,
            author=author,
            status=Article.Status.PUBLISHED,
            published_at=published_at,
        )
        article.tags.add(tag)

        response = self.client.get(f"/article/{article.slug}")

        self.assertEqual(response.status_code, 200)
        rendered = response.content.decode()
        schema_match = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            rendered,
        )
        self.assertIsNotNone(schema_match)
        schema = json.loads(schema_match.group(1))
        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "NewsArticle")
        self.assertEqual(schema["headline"], article.title)
        self.assertEqual(schema["datePublished"], published_at.isoformat())
        self.assertEqual(schema["author"]["@type"], "Person")
        self.assertEqual(schema["author"]["name"], author.name)
        self.assertEqual(schema["author"]["url"], f"https://fxlfm.com/author/{author.slug}")
        self.assertEqual(schema["mainEntityOfPage"]["@id"], f"https://fxlfm.com/article/{article.slug}")
        self.assertEqual(schema["image"], [article.image_url])
        self.assertEqual(schema["articleSection"], category.name)
        self.assertEqual(schema["keywords"], tag.name)
        self.assertIn('data-server-rendered="article"', rendered)
        self.assertIn(f"<h1 class=\"font-display text-4xl md:text-5xl mt-3\">{article.title}</h1>", rendered)
        self.assertIn("First server-rendered paragraph.", rendered)
        self.assertIn("Second paragraph with &lt;script&gt;alert", rendered)
        self.assertNotIn("<script>alert('x')</script>", rendered)
        self.assertIn(f"By {author.name}", rendered)
        self.assertIn(f'href="/author/{author.slug}"', rendered)
        self.assertNotIn('<div id="root"></div>', rendered)


class AuthorPageTests(TestCase):
    @patch("apps.news.seo_views.requests.get")
    def test_author_profile_has_ssr_content_api_and_person_schema(self, mock_get):
        frontend_response = Mock()
        frontend_response.text = """
            <html><head>
              <meta name="seo-head-start" content="" />
              <title>Default title</title>
              <meta name="seo-head-end" content="" />
            </head><body><div id="root"></div></body></html>
        """
        frontend_response.raise_for_status.return_value = None
        mock_get.return_value = frontend_response

        author, _ = Author.objects.update_or_create(
            slug="maria-nicholson",
            defaults={
                "name": "Maria Nicholson",
                "job_title": "Senior News Editor",
                "bio": "Maria Nicholson covers global affairs, technology and business.",
                "photo_url": "https://images.example.com/maria.jpg",
                "location": "London, United Kingdom",
                "x_url": "https://x.com/marianicholsonnews",
                "linkedin_url": "https://www.linkedin.com/in/maria-nicholson-news/",
                "instagram_url": "https://www.instagram.com/marianicholson.news/",
                "joined_at": "2024-03-18",
            },
        )
        category = Category.objects.create(name="World")
        article = Article.objects.create(
            title="Maria's Published Story",
            original_title="Maria's Published Story",
            original_content="Story content",
            summary="Story summary",
            source_name="Unit Test",
            source_url="https://example.com/news/author-page",
            category=category,
            author=author,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        page_response = self.client.get(f"/author/{author.slug}")
        api_response = self.client.get(f"/api/authors/{author.slug}/")

        self.assertEqual(page_response.status_code, 200)
        rendered = page_response.content.decode()
        self.assertIn('data-server-rendered="author"', rendered)
        self.assertIn(author.name, rendered)
        self.assertIn(author.bio, rendered)
        self.assertIn(author.photo_url.replace("&", "&amp;"), rendered)
        self.assertIn(article.title.replace("'", "&#x27;"), rendered)
        schema_match = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            rendered,
        )
        schema = json.loads(schema_match.group(1))
        self.assertEqual(schema["@type"], "Person")
        self.assertEqual(schema["name"], author.name)
        self.assertEqual(schema["sameAs"], [author.x_url, author.linkedin_url, author.instagram_url])

        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.data["name"], author.name)
        self.assertEqual(api_response.data["articles"][0]["slug"], article.slug)


class SitemapTests(TestCase):
    def test_sitemap_contains_published_content_and_excludes_drafts(self):
        published_category = Category.objects.create(name="Technology")
        empty_category = Category.objects.create(name="Empty")
        author = Author.objects.get(slug="maria-nicholson")
        published = Article.objects.create(
            title="Published Article",
            original_title="Published Article",
            original_content="Published content",
            source_name="Unit Test",
            source_url="https://example.com/news/published",
            category=published_category,
            author=author,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        draft = Article.objects.create(
            title="Draft Article",
            original_title="Draft Article",
            original_content="Draft content",
            source_name="Unit Test",
            source_url="https://example.com/news/draft",
            category=empty_category,
            status=Article.Status.DRAFT,
        )

        response = self.client.get("/sitemap.xml")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        root = ElementTree.fromstring(response.content)
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {element.text for element in root.findall("sm:url/sm:loc", namespace)}
        self.assertIn(f"https://fxlfm.com/article/{published.slug}", locations)
        self.assertNotIn(f"https://fxlfm.com/article/{draft.slug}", locations)
        self.assertIn(f"https://fxlfm.com/category/{published_category.slug}", locations)
        self.assertIn(f"https://fxlfm.com/author/{author.slug}", locations)
        self.assertNotIn(f"https://fxlfm.com/category/{empty_category.slug}", locations)
        self.assertIn("https://fxlfm.com/", locations)
        self.assertIn("https://fxlfm.com/about", locations)
        self.assertIn("https://fxlfm.com/contact", locations)
        self.assertNotIn("https://fxlfm.com/search", locations)

    def test_robots_txt_points_to_sitemap(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        content = response.content.decode()
        self.assertIn("User-agent: *", content)
        self.assertIn("Sitemap: https://fxlfm.com/sitemap.xml", content)
