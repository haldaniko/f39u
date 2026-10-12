"""Narrow publishing API for an external editorial bot."""

from __future__ import annotations

import hashlib
import io
import json
from uuid import UUID

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework import permissions, serializers, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .categories import CANONICAL_CATEGORY_SLUGS
from .models import Article, Author, Category
from .serializers import AdminArticleSerializer
from .services import NewsQueryService


class HasBotIntegrationToken(permissions.BasePermission):
    def has_permission(self, request, view):
        expected = settings.BOT_INTEGRATION_TOKEN
        authorization = request.headers.get("Authorization", "")
        return bool(expected) and authorization.startswith("Bearer ") and constant_time_compare(
            authorization[7:], expected
        )


class BotArticleInputSerializer(serializers.Serializer):
    external_id = serializers.UUIDField()
    title = serializers.CharField(max_length=300)
    content = serializers.CharField()
    summary = serializers.CharField(required=False, allow_blank=True)
    seo_description = serializers.CharField(max_length=320, required=False, allow_blank=True)
    category_slugs = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.filter(slug__in=CANONICAL_CATEGORY_SLUGS),
        many=True,
        allow_empty=False,
    )
    author_slug = serializers.SlugRelatedField(
        slug_field="slug", queryset=Author.objects.all(), required=False, allow_null=True
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=80), required=False, allow_empty=True
    )


def _payload_hash(data):
    canonical = {
        "title": data["title"],
        "content": data["content"],
        "summary": data.get("summary", ""),
        "seo_description": data.get("seo_description", ""),
        "category_slugs": [category.slug for category in data["category_slugs"]],
        "author_slug": data["author_slug"].slug if data.get("author_slug") else None,
        "tag_names": data.get("tag_names", []),
    }
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _article_response(article):
    return {
        "external_id": str(article.integration_id),
        "article_id": article.pk,
        "status": article.status,
        "slug": article.slug,
        "url": f"{settings.SITE_URL}/article/{article.slug}",
        "image_url": article.image_url,
    }


def _get_article(external_id: UUID):
    try:
        return Article.objects.get(integration_id=external_id)
    except Article.DoesNotExist as exc:
        raise Http404 from exc


class BotOptionsView(APIView):
    authentication_classes = []
    permission_classes = [HasBotIntegrationToken]

    def get(self, request):
        NewsQueryService.normalize_category_aliases()
        categories = Category.objects.filter(slug__in=CANONICAL_CATEGORY_SLUGS)
        by_slug = {category.slug: category for category in categories}
        return Response(
            {
                "version": 1,
                "site": "fxlfm",
                "categories": [
                    {"slug": slug, "name": by_slug[slug].name}
                    for slug in CANONICAL_CATEGORY_SLUGS
                    if slug in by_slug
                ],
                "authors": list(Author.objects.order_by("name").values("slug", "name")),
            }
        )


class BotArticlesView(APIView):
    authentication_classes = []
    permission_classes = [HasBotIntegrationToken]
    parser_classes = [JSONParser]

    def post(self, request):
        data = BotArticleInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        external_id = values["external_id"]
        payload_hash = _payload_hash(values)
        existing = Article.objects.filter(integration_id=external_id).first()
        if existing:
            return self._existing_response(existing, payload_hash)

        categories = values["category_slugs"]
        article_data = {
            "title": values["title"],
            "rewritten_content": values["content"],
            "summary": values.get("summary", ""),
            "seo_description": values.get("seo_description", ""),
            "category_ids": [category.pk for category in categories],
            "author_id": values["author_slug"].pk if values.get("author_slug") else None,
            "tag_names": values.get("tag_names", []),
            "status": Article.Status.DRAFT,
        }
        serializer = AdminArticleSerializer(data=article_data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                article = serializer.save(
                    integration_id=external_id,
                    integration_payload_hash=payload_hash,
                )
        except IntegrityError:
            existing = Article.objects.filter(integration_id=external_id).first()
            if existing is None:
                raise
            return self._existing_response(existing, payload_hash)
        return Response(_article_response(article), status=status.HTTP_201_CREATED)

    @staticmethod
    def _existing_response(article, payload_hash):
        if article.integration_payload_hash != payload_hash:
            return Response(
                {"detail": "external_id already belongs to a different article payload."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(_article_response(article))


class BotArticleDetailView(APIView):
    authentication_classes = []
    permission_classes = [HasBotIntegrationToken]

    def get(self, request, external_id):
        return Response(_article_response(_get_article(external_id)))


class BotArticleImageView(APIView):
    authentication_classes = []
    permission_classes = [HasBotIntegrationToken]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, external_id):
        upload = request.FILES.get("image")
        if upload is None:
            return Response({"image": "Upload an image file."}, status=400)
        if upload.size > 10 * 1024 * 1024:
            return Response({"image": "Image must be 10 MB or smaller."}, status=400)
        try:
            with Image.open(upload) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValueError("Unsupported image format")
                if source.width * source.height > 20_000_000:
                    raise ValueError("Image dimensions are too large")
                image = ImageOps.exif_transpose(source)
                rgba = image.convert("RGBA")
                normalized = Image.new("RGB", rgba.size, "white")
                normalized.paste(rgba, mask=rgba.getchannel("A"))
                output = io.BytesIO()
                normalized.save(output, format="JPEG", quality=88, optimize=True)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            return Response({"image": "Upload a valid JPG, PNG or WebP image."}, status=400)

        with transaction.atomic():
            article = Article.objects.select_for_update().filter(integration_id=external_id).first()
            if article is None:
                raise Http404
            if article.status != Article.Status.DRAFT:
                return Response({"detail": "Only a draft article can receive an image."}, status=409)
            if article.bot_image:
                return Response(_article_response(article))
            article.bot_image.save(f"{external_id}.jpg", ContentFile(output.getvalue()), save=False)
            article.image_url = f"{settings.SITE_URL}/api/article-images/{external_id}/"
            article.save(update_fields=["bot_image", "image_url", "updated_at"])
        return Response(_article_response(article))


class BotArticlePublishView(APIView):
    authentication_classes = []
    permission_classes = [HasBotIntegrationToken]

    def post(self, request, external_id):
        with transaction.atomic():
            article = Article.objects.select_for_update().filter(integration_id=external_id).first()
            if article is None:
                raise Http404
            if article.status == Article.Status.PUBLISHED:
                return Response(_article_response(article))
            if article.status != Article.Status.DRAFT:
                return Response({"detail": "Only a draft article can be published through this API."}, status=409)
            if not article.title.strip() or not article.rewritten_content.strip() or not article.categories.exists():
                return Response({"detail": "Title, content and category are required."}, status=400)
            article.status = Article.Status.PUBLISHED
            article.published_at = timezone.now()
            article.save(update_fields=["status", "published_at", "updated_at"])
        return Response(_article_response(article))


@require_GET
def bot_article_image(request, external_id):
    article = Article.objects.filter(
        integration_id=external_id, status=Article.Status.PUBLISHED
    ).first()
    if article is None or not article.bot_image:
        raise Http404
    return FileResponse(article.bot_image.open("rb"), content_type="image/jpeg")
