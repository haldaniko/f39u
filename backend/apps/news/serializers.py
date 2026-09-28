from __future__ import annotations

from uuid import uuid4

from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from .models import Article, Author, Category, NewsletterSubscriber, Tag


class AuthorSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

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

    def get_photo_url(self, obj):
        url = obj.display_photo_url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if url and request and url.startswith("/") else url


class AdminAuthorSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    photo = serializers.FileField(write_only=True, required=False)
    remove_photo = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Author
        fields = [
            "id",
            "name",
            "slug",
            "job_title",
            "bio",
            "photo",
            "photo_url",
            "remove_photo",
            "location",
            "x_url",
            "linkedin_url",
            "instagram_url",
            "joined_at",
        ]
        read_only_fields = ["id", "slug"]

    def validate_name(self, value):
        queryset = Author.objects.filter(name__iexact=value.strip())
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("An editor with this name already exists.")
        return value.strip()

    def get_photo_url(self, obj):
        url = obj.display_photo_url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if url and request and url.startswith("/") else url

    def validate_photo(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("The photo must be no larger than 5 MB.")
        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if getattr(value, "content_type", "") not in allowed_types:
            raise serializers.ValidationError("Upload a JPG, PNG or WebP image.")
        return value

    def create(self, validated_data):
        validated_data.pop("remove_photo", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove_photo = validated_data.pop("remove_photo", False)
        replacement = validated_data.get("photo")
        old_photo_name = instance.photo.name if instance.photo else ""
        old_storage = instance.photo.storage if instance.photo else None

        if remove_photo and replacement is None:
            validated_data["photo"] = ""

        author = super().update(instance, validated_data)
        if old_photo_name and (remove_photo or replacement is not None):
            old_storage.delete(old_photo_name)
        return author


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    total = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ["name", "slug", "description", "total"]


class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    source = serializers.ChoiceField(
        choices=NewsletterSubscriber.Source.choices,
        default=NewsletterSubscriber.Source.FOOTER,
    )

    def validate_email(self, value):
        return value.strip().lower()


class AdminNewsletterSubscriberSerializer(serializers.ModelSerializer):
    source_label = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = NewsletterSubscriber
        fields = [
            "id",
            "email",
            "source",
            "source_label",
            "is_active",
            "subscribed_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "source", "source_label", "subscribed_at", "updated_at"]


class ArticleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "title",
            "slug",
            "summary",
            "rewritten_content",
            "image_url",
            "source_name",
            "published_at",
            "category",
            "categories",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
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
            "categories",
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
    categories = CategorySerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        source="categories",
        queryset=Category.objects.all(),
        many=True,
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
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=80),
        write_only=True,
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
            "categories",
            "category_id",
            "category_ids",
            "author",
            "author_id",
            "tags",
            "tag_ids",
            "tag_names",
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
        categories = validated_data.get("categories")
        category = validated_data.get("category", instance.category if instance else None)
        has_categories = bool(categories) or bool(category) or (instance is not None and instance.categories.exists())
        if status == Article.Status.PUBLISHED and not has_categories:
            raise serializers.ValidationError({"category_ids": "Select at least one category before publishing."})
        if status == Article.Status.PUBLISHED and not validated_data.get(
            "published_at",
            instance.published_at if instance else None,
        ):
            validated_data["published_at"] = timezone.now()
        return validated_data

    @staticmethod
    def _resolve_tags(tag_names):
        tags = []
        seen = set()
        for raw_name in tag_names:
            name = raw_name.strip().lstrip("#").strip()
            key = name.casefold()
            if not name or key in seen:
                continue
            seen.add(key)
            tag = Tag.objects.filter(name__iexact=name).first()
            if tag is None:
                base_slug = slugify(name)[:90] or f"tag-{uuid4().hex[:8]}"
                slug = base_slug
                suffix = 2
                while Tag.objects.filter(slug=slug).exists():
                    slug = f"{base_slug[:95]}-{suffix}"
                    suffix += 1
                tag = Tag.objects.create(name=name, slug=slug)
            tags.append(tag)
        return tags

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        tags = validated_data.pop("tags", [])
        if tag_names is not None:
            tags = self._resolve_tags(tag_names)
        categories = validated_data.pop("categories", [])
        if categories and not validated_data.get("category"):
            validated_data["category"] = categories[0]
        article = Article.objects.create(**self._prepare_editorial_fields(validated_data))
        article.categories.set(categories or ([article.category] if article.category else []))
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        tags = validated_data.pop("tags", None)
        if tag_names is not None:
            tags = self._resolve_tags(tag_names)
        categories = validated_data.pop("categories", None)
        if categories is not None and categories and "category" not in validated_data:
            validated_data["category"] = categories[0]
        article = super().update(
            instance,
            self._prepare_editorial_fields(validated_data, instance=instance),
        )
        if categories is not None:
            article.categories.set(categories or ([article.category] if article.category else []))
        if tags is not None:
            article.tags.set(tags)
        return article
