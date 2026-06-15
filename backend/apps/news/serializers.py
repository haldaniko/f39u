from __future__ import annotations

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
