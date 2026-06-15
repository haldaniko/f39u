from django.test import SimpleTestCase, TestCase

from .models import Article, Category
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
        )

        rendered = SEO_BLOCK_PATTERN.sub(seo_head, index_html, count=1)

        self.assertNotIn("Default title", rendered)
        self.assertIn("Markets &amp; &quot;Technology&quot; | FXLFM", rendered)
        self.assertIn("News about markets &amp; technology.", rendered)
        self.assertIn('property="og:type" content="article"', rendered)
        self.assertIn('property="article:published_time"', rendered)
        self.assertIn('rel="canonical" href="https://fxlfm.com/article/markets-technology"', rendered)

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
