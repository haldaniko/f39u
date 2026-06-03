from django.test import TestCase

from apps.news.models import Article, Category

from .services import RewriteService


class RewriteServiceTests(TestCase):
    def test_rewrite_changes_status(self):
        category = Category.objects.create(name="General")
        Article.objects.create(
            title="Original",
            original_title="Original",
            original_content="Some news content.",
            source_name="Example",
            source_url="https://example.com/ai-test",
            category=category,
        )
        updated = RewriteService().rewrite_pending_articles(limit=1)
        self.assertEqual(updated, 1)
