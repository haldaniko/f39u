from django.test import TestCase
from unittest.mock import patch

from apps.news.models import Article, Category
from apps.ai.providers import OpenRouterRewriter

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
                    "OPENROUTER_MAX_INPUT_CHARS": "12000",
                    "OPENROUTER_MAX_OUTPUT_TOKENS": "900",
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
