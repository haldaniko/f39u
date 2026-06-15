from __future__ import annotations

from rest_framework import serializers

from .models import Article, Category, Tag


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
            "tags",
        ]
