from django.test import TestCase
from unittest.mock import Mock, patch

from apps.news.models import Article, Category
from apps.ai.providers import OpenRouterRewriter

from .services import RewriteService


class RewriteServiceTests(TestCase):
    @patch("apps.ai.services.get_ai_rewriter")
    def test_rewrite_changes_status(self, mock_get_rewriter):
        body = "\n\n".join(
            [
                " ".join(
                    [
                        "This is a complete rewritten paragraph with enough newsroom detail to pass the publishing quality gate."
                    ]
                    * 5
                ),
                " ".join(
                    [
                        "The second paragraph adds more context and keeps the story readable without relying on teaser copy."
                    ]
                    * 5
                ),
                " ".join(
                    [
                        "The third paragraph closes the report with a concise explanation of the wider significance for readers."
                    ]
                    * 5
                ),
            ]
        )
        mock_get_rewriter.return_value = Mock(
            rewrite=Mock(
                return_value={
                    "title": "Rewritten title",
                    "summary": "A reliable rewritten summary.",
                    "body": body,
                    "seo_description": "A reliable rewritten summary.",
                    "tags": ["news"],
                    "_fallback": "false",
                }
            )
        )
        category = Category.objects.create(name="General")
        article = Article.objects.create(
            title="Original",
            original_title="Original",
            original_content=" ".join(["Some news content with enough source detail."] * 20),
            source_name="Example",
            source_url="https://example.com/ai-test",
            category=category,
        )
        updated = RewriteService().rewrite_pending_articles(limit=1)
        self.assertEqual(updated, 1)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.PUBLISHED)
        self.assertEqual(article.rewritten_title, "Rewritten title")

    def test_rewrite_rejects_empty_source_content(self):
        category = Category.objects.create(name="General")
        article = Article.objects.create(
            title="Original",
            original_title="Original",
            original_content="",
            source_name="Example",
            source_url="https://example.com/ai-empty-source",
            category=category,
        )

        updated = RewriteService().rewrite_pending_articles(limit=1)

        self.assertEqual(updated, 0)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.REJECTED)

    @patch("apps.ai.services.get_ai_rewriter")
    def test_rewrite_does_not_publish_fallback_result(self, mock_get_rewriter):
        mock_get_rewriter.return_value = Mock(
            rewrite=Mock(
                return_value={
                    "title": "Original",
                    "summary": "Fallback summary",
                    "body": " ".join(["Fallback body"] * 120),
                    "seo_description": "Fallback summary",
                    "tags": ["news"],
                    "_fallback": "true",
                }
            )
        )
        category = Category.objects.create(name="General")
        article = Article.objects.create(
            title="Original",
            original_title="Original",
            original_content=" ".join(["Some news content with enough source detail."] * 20),
            source_name="Example",
            source_url="https://example.com/ai-fallback",
            category=category,
        )

        updated = RewriteService().rewrite_pending_articles(limit=1)

        self.assertEqual(updated, 0)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.PENDING_REVIEW)


class OpenRouterRewriterTests(TestCase):
    @patch("apps.ai.providers.requests.post")
    def test_rewrite_prompt_enforces_english_output_for_non_english_sources(self, mock_post):
        class _MockResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": '{"title":"Title","summary":"Summary","body":"Body","seo_description":"SEO","tags":["news"]}'
                            }
                        }
                    ]
                }

        mock_post.return_value = _MockResponse()

        with patch("apps.ai.providers.os.getenv") as mock_getenv:
            def _getenv(name, default=None):
                values = {
                    "OPENROUTER_API_KEY": "test-key",
                    "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1/chat/completions",
                    "OPENROUTER_MODEL": "openai/gpt-4o-mini",
                    "OPENROUTER_TIMEOUT": "45",
                    "OPENROUTER_MAX_INPUT_CHARS": "16000",
                    "OPENROUTER_MAX_OUTPUT_TOKENS": "2200",
                    "OPENROUTER_TEMPERATURE": "0.3",
                    "OPENROUTER_SITE_URL": "",
                    "OPENROUTER_APP_NAME": "FXLFM",
                }
                return values.get(name, default)

            mock_getenv.side_effect = _getenv
            rewriter = OpenRouterRewriter()
            rewriter.rewrite({"title": "Noticias", "content": "Texto en espanol."})

        payload = mock_post.call_args.kwargs["json"]
        user_prompt = payload["messages"][1]["content"]
        self.assertIn("if it is not English, translate the final", user_prompt)
        self.assertIn("Separate each paragraph with a blank line", user_prompt)
        self.assertEqual(payload["max_tokens"], 2200)
