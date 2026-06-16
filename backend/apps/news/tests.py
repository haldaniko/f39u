import json
import re
from unittest.mock import Mock, patch
from xml.etree import ElementTree

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Article, ArticleSlugRedirect, Author, Category, Tag
from .seo_views import SEO_BLOCK_PATTERN, _seo_head


class FrontendAdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            username="editor",
            password="strong-test-password",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="reader",
            password="strong-test-password",
        )
        self.category = Category.objects.create(name="Editorial")
        self.author = Author.objects.get(slug="maria-nicholson")
        self.tag = Tag.objects.create(name="Exclusive")

    def authenticate_staff(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": self.staff.username, "password": "strong-test-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_admin_endpoints_require_staff_access(self):
        anonymous_response = self.client.get("/api/admin/articles/")
        regular_login = self.client.post(
            "/api/auth/login/",
            {"username": self.regular_user.username, "password": "strong-test-password"},
            format="json",
        )

        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(regular_login.status_code, 400)

    def test_staff_can_create_publish_update_and_delete_article(self):
        self.authenticate_staff()
        create_response = self.client.post(
            "/api/admin/articles/",
            {
                "title": "Original Reporting from the FXLFM Newsroom",
                "summary": "A concise editorial summary.",
                "rewritten_content": "First paragraph.\n\nSecond paragraph.",
                "seo_description": "Original reporting and analysis from the FXLFM newsroom.",
                "status": Article.Status.PUBLISHED,
                "category_id": self.category.pk,
                "author_id": self.author.pk,
                "tag_ids": [self.tag.pk],
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, 201, create_response.data)
        article = Article.objects.get(pk=create_response.data["id"])
        self.assertEqual(article.original_title, article.title)
        self.assertEqual(article.original_content, article.rewritten_content)
        self.assertEqual(article.source_name, "FXLFM Editorial")
        self.assertTrue(article.source_url.startswith("https://fxlfm.com/editorial/"))
        self.assertIsNotNone(article.published_at)
        self.assertEqual(list(article.tags.all()), [self.tag])

        update_response = self.client.patch(
            f"/api/admin/articles/{article.pk}/",
            {"summary": "An updated summary."},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        article.refresh_from_db()
        self.assertEqual(article.summary, "An updated summary.")
        self.assertEqual(article.source_name, "FXLFM Editorial")

        delete_response = self.client.delete(f"/api/admin/articles/{article.pk}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Article.objects.filter(pk=article.pk).exists())

    def test_staff_can_load_editor_options(self):
        self.authenticate_staff()
        response = self.client.get("/api/admin/options/")

        self.assertEqual(response.status_code, 200)
        self.assertIn({"value": "published", "label": "Published"}, response.data["statuses"])
        self.assertEqual(response.data["categories"][0]["id"], self.category.pk)
        self.assertEqual(response.data["authors"][0]["id"], self.author.pk)
        self.assertEqual(response.data["tags"][0]["id"], self.tag.pk)


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

    def test_article_slug_is_readable_and_uses_numeric_collision_suffix(self):
        category = Category.objects.create(name="Business")
        first = Article.objects.create(
            title="Elon Musk Net Worth 2026",
            original_title="Elon Musk Net Worth 2026",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/slug-1",
            category=category,
        )
        second = Article.objects.create(
            title="Elon Musk Net Worth 2026",
            original_title="Elon Musk Net Worth 2026",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/slug-2",
            category=category,
        )

        self.assertEqual(first.slug, "elon-musk-net-worth-2026")
        self.assertEqual(second.slug, "elon-musk-net-worth-2026-2")

    def test_article_slug_transliterates_non_latin_title(self):
        category = Category.objects.create(name="World")
        article = Article.objects.create(
            title="Зеленски предложил встречу",
            original_title="Зеленски предложил встречу",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/transliterated-slug",
            category=category,
        )

        self.assertEqual(article.slug, "zelenski-predlozhil-vstrechu")

    def test_new_article_does_not_reuse_reserved_legacy_slug(self):
        category = Category.objects.create(name="Reserved Slug")
        existing = Article.objects.create(
            title="Existing Story",
            original_title="Existing Story",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/reserved-existing",
            category=category,
        )
        ArticleSlugRedirect.objects.create(old_slug="reserved-news-story", article=existing)

        article = Article.objects.create(
            title="Reserved News Story",
            original_title="Reserved News Story",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/reserved-new",
            category=category,
        )

        self.assertEqual(article.slug, "reserved-news-story-2")

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

    def test_legacy_article_slug_permanently_redirects_to_clean_url(self):
        category = Category.objects.create(name="Technology Redirect")
        article = Article.objects.create(
            title="Elon Musk Net Worth 2026",
            original_title="Elon Musk Net Worth 2026",
            original_content="content",
            source_name="Unit Test",
            source_url="https://example.com/news/legacy-redirect",
            category=category,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        ArticleSlugRedirect.objects.create(
            old_slug="who-is-elon-musk-61e76fda4b",
            article=article,
        )

        response = self.client.get("/article/who-is-elon-musk-61e76fda4b")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], f"/article/{article.slug}")


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


class RelatedStoriesTests(TestCase):
    @patch("apps.news.seo_views.requests.get")
    def test_related_stories_prioritize_tags_then_category_and_render_in_ssr(self, mock_get):
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

        author = Author.objects.get(slug="maria-nicholson")
        technology = Category.objects.create(name="Technology")
        business = Category.objects.create(name="Business")
        ai_tag = Tag.objects.create(name="Artificial Intelligence")
        published_at = timezone.now()

        target = Article.objects.create(
            title="Target AI Story",
            original_title="Target AI Story",
            original_content="Target content",
            source_name="Unit Test",
            source_url="https://example.com/news/related-target",
            category=technology,
            author=author,
            status=Article.Status.PUBLISHED,
            published_at=published_at,
        )
        target.tags.add(ai_tag)
        tag_match = Article.objects.create(
            title="AI Investment Expands",
            original_title="AI Investment Expands",
            original_content="Tag match content",
            source_name="Unit Test",
            source_url="https://example.com/news/related-tag",
            category=business,
            author=author,
            status=Article.Status.PUBLISHED,
            published_at=published_at,
        )
        tag_match.tags.add(ai_tag)
        category_match = Article.objects.create(
            title="Technology Sector Update",
            original_title="Technology Sector Update",
            original_content="Category match content",
            source_name="Unit Test",
            source_url="https://example.com/news/related-category",
            category=technology,
            author=author,
            status=Article.Status.PUBLISHED,
            published_at=published_at,
        )
        draft_match = Article.objects.create(
            title="Draft AI Story",
            original_title="Draft AI Story",
            original_content="Draft content",
            source_name="Unit Test",
            source_url="https://example.com/news/related-draft",
            category=technology,
            author=author,
            status=Article.Status.DRAFT,
        )
        draft_match.tags.add(ai_tag)

        api_response = self.client.get(f"/api/news/{target.slug}/related/")
        page_response = self.client.get(f"/article/{target.slug}")

        self.assertEqual(api_response.status_code, 200)
        related_slugs = [item["slug"] for item in api_response.data]
        self.assertEqual(related_slugs[:2], [tag_match.slug, category_match.slug])
        self.assertNotIn(target.slug, related_slugs)
        self.assertNotIn(draft_match.slug, related_slugs)

        rendered = page_response.content.decode()
        self.assertIn("Related Stories", rendered)
        self.assertIn(f'href="/article/{tag_match.slug}"', rendered)
        self.assertIn(f'href="/article/{category_match.slug}"', rendered)
        self.assertNotIn(f'href="/article/{draft_match.slug}"', rendered)


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
