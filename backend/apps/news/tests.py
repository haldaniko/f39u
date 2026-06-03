from django.test import TestCase

from .models import Article, Category


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
