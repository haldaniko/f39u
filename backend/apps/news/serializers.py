from __future__ import annotations

from uuid import uuid4

from django.utils import timezone
from rest_framework import serializers

from .models import Article, Author, Category, Tag


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "name",
            "slug",
            "job_title",
            "bio",
            "photo_url",
            "location",
            "x_url",
            "linkedin_url",
            "instagram_url",
            "joined_at",
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug", "description"]


class ArticleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "title",
            "slug",
            "summary",
            "image_url",
            "source_name",
            "published_at",
            "category",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "title",
            "slug",
            "summary",
            "rewritten_content",
            "seo_description",
            "image_url",
            "source_name",
            "source_url",
            "published_at",
            "created_at",
            "updated_at",
            "category",
            "author",
            "tags",
        ]


class AuthorDetailSerializer(AuthorSerializer):
    articles = serializers.SerializerMethodField()

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ["articles"]

    def get_articles(self, author: Author):
        queryset = author.articles.filter(status=Article.Status.PUBLISHED).select_related("category")[:50]
        return ArticleListSerializer(queryset, many=True).data


class AdminArticleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        source="author",
        queryset=Author.objects.all(),
        allow_null=True,
        required=False,
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags",
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )
    source_name = serializers.CharField(required=False, allow_blank=True)
    source_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "rewritten_content",
            "seo_description",
            "image_url",
            "source_name",
            "source_url",
            "published_at",
            "status",
            "category",
            "category_id",
            "author",
            "author_id",
            "tags",
            "tag_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def _prepare_editorial_fields(self, validated_data, instance=None):
        title = validated_data.get("title", instance.title if instance else "")
        content = validated_data.get(
            "rewritten_content",
            instance.rewritten_content if instance else "",
        )
        validated_data["original_title"] = title
        validated_data["rewritten_title"] = title
        validated_data["original_content"] = content

        if instance is None and not validated_data.get("source_name"):
            validated_data["source_name"] = "FXLFM Editorial"
        elif "source_name" in validated_data and not validated_data["source_name"]:
            validated_data["source_name"] = "FXLFM Editorial"
        if instance is None and not validated_data.get("source_url"):
            validated_data["source_url"] = f"https://fxlfm.com/editorial/{uuid4()}"
        elif instance is not None and not validated_data.get("source_url"):
            validated_data.pop("source_url", None)

        status = validated_data.get("status", instance.status if instance else Article.Status.DRAFT)
        if status == Article.Status.PUBLISHED and not validated_data.get(
            "published_at",
            instance.published_at if instance else None,
        ):
            validated_data["published_at"] = timezone.now()
        return validated_data

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        article = Article.objects.create(**self._prepare_editorial_fields(validated_data))
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        article = super().update(
            instance,
            self._prepare_editorial_fields(validated_data, instance=instance),
        )
        if tags is not None:
            article.tags.set(tags)
        return article
