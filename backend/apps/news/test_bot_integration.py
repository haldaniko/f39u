import io
import tempfile
from uuid import uuid4

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from .models import Article, Category


@override_settings(BOT_INTEGRATION_TOKEN="test-integration-secret", SITE_URL="https://fxlfm.com")
class BotIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.external_id = uuid4()
        self.category = Category.objects.get(slug="politics")
        self.payload = {
            "external_id": str(self.external_id),
            "title": "A newsroom article from Telegram",
            "content": "First paragraph.\n\nSecond paragraph.",
            "summary": "A short introduction.",
            "category_slugs": [self.category.slug],
            "tag_names": ["Exclusive"],
        }

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer test-integration-secret")

    def test_requires_dedicated_token(self):
        self.assertEqual(self.client.get("/api/bot/v1/options/").status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer wrong-token")
        self.assertEqual(self.client.post("/api/bot/v1/articles/", self.payload, format="json").status_code, 403)
        self.assertFalse(Article.objects.filter(integration_id=self.external_id).exists())

    @override_settings(BOT_INTEGRATION_TOKEN="")
    def test_api_is_disabled_without_configured_token(self):
        self.authenticate()
        self.assertEqual(self.client.get("/api/bot/v1/options/").status_code, 403)

    def test_options_and_idempotent_publication(self):
        self.authenticate()
        options = self.client.get("/api/bot/v1/options/")
        self.assertEqual(options.status_code, 200)
        self.assertIn({"slug": self.category.slug, "name": self.category.name}, options.data["categories"])

        first = self.client.post("/api/bot/v1/articles/", self.payload, format="json")
        retry = self.client.post("/api/bot/v1/articles/", self.payload, format="json")
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(retry.status_code, 200, retry.data)
        self.assertEqual(first.data["article_id"], retry.data["article_id"])
        self.assertEqual(Article.objects.filter(integration_id=self.external_id).count(), 1)
        article = Article.objects.get(integration_id=self.external_id)
        self.assertEqual(article.status, Article.Status.DRAFT)
        self.assertEqual(article.rewritten_content, self.payload["content"])
        self.assertEqual(list(article.categories.values_list("slug", flat=True)), [self.category.slug])

        detail = self.client.get(f"/api/bot/v1/articles/{self.external_id}/")
        self.assertEqual(detail.status_code, 200)
        publish_url = f"/api/bot/v1/articles/{self.external_id}/publish/"
        published = self.client.post(publish_url)
        republished = self.client.post(publish_url)
        self.assertEqual(published.status_code, 200)
        self.assertEqual(republished.status_code, 200)
        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.PUBLISHED)
        self.assertEqual(published.data["url"], f"https://fxlfm.com/article/{article.slug}")
        self.assertEqual(Article.objects.filter(integration_id=self.external_id).count(), 1)

    def test_reusing_external_id_with_other_content_is_rejected(self):
        self.authenticate()
        self.assertEqual(self.client.post("/api/bot/v1/articles/", self.payload, format="json").status_code, 201)
        changed = {**self.payload, "content": "Different content"}
        response = self.client.post("/api/bot/v1/articles/", changed, format="json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Article.objects.filter(integration_id=self.external_id).count(), 1)

    def test_invalid_category_is_rejected(self):
        self.authenticate()
        payload = {**self.payload, "category_slugs": ["missing-category"]}
        response = self.client.post("/api/bot/v1/articles/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Article.objects.filter(integration_id=self.external_id).exists())

    def test_photo_is_stored_and_served_after_publication(self):
        self.authenticate()
        create = self.client.post("/api/bot/v1/articles/", self.payload, format="json")
        self.assertEqual(create.status_code, 201, create.data)
        image_url = f"/api/bot/v1/articles/{self.external_id}/image/"
        image = Image.new("RGB", (16, 16), "blue")
        content = io.BytesIO()
        image.save(content, format="PNG")
        image_bytes = content.getvalue()
        content.seek(0)

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            unpublished = self.client.get(f"/api/article-images/{self.external_id}/")
            self.assertEqual(unpublished.status_code, 404)
            uploaded = self.client.put(image_url, {"image": content}, format="multipart")
            self.assertEqual(uploaded.status_code, 200, uploaded.data)
            retry = self.client.put(
                image_url,
                {"image": SimpleUploadedFile("retry.png", image_bytes, content_type="image/png")},
                format="multipart",
            )
            self.assertEqual(retry.status_code, 200, retry.data)
            self.assertEqual(retry.data["image_url"], uploaded.data["image_url"])
            self.assertEqual(
                uploaded.data["image_url"], f"https://fxlfm.com/api/article-images/{self.external_id}/"
            )
            article = Article.objects.get(integration_id=self.external_id)
            self.assertTrue(article.bot_image.name.endswith(".jpg"))
            self.assertEqual(self.client.post(f"/api/bot/v1/articles/{self.external_id}/publish/").status_code, 200)
            public_image = self.client.get(f"/api/article-images/{self.external_id}/")
            self.assertEqual(public_image.status_code, 200)
            self.assertEqual(public_image["Content-Type"], "image/jpeg")
            self.assertTrue(b"".join(public_image.streaming_content).startswith(b"\xff\xd8"))

    def test_invalid_photo_is_rejected(self):
        self.authenticate()
        self.client.post("/api/bot/v1/articles/", self.payload, format="json")
        response = self.client.put(
            f"/api/bot/v1/articles/{self.external_id}/image/",
            {"image": io.BytesIO(b"not-an-image")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)
