from __future__ import annotations

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

from .slug_utils import unique_article_slug


class Author(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    job_title = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True)
    photo = models.FileField(
        upload_to="authors/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    photo_url = models.URLField(max_length=500, blank=True)
    location = models.CharField(max_length=160, blank=True)
    x_url = models.URLField(max_length=500, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True)
    instagram_url = models.URLField(max_length=500, blank=True)
    joined_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @property
    def display_photo_url(self) -> str:
        if self.photo:
            return self.photo.url
        return self.photo_url


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=120, unique=True)
    provider = models.CharField(max_length=80)
    enabled = models.BooleanField(default=True)
    base_url = models.URLField(blank=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.provider})"


class NewsletterSubscriber(models.Model):
    class Source(models.TextChoices):
        FOOTER = "footer", "Footer"
        POPUP = "popup", "Popup"

    email = models.EmailField(unique=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.FOOTER)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-subscribed_at"]
        indexes = [models.Index(fields=["is_active", "subscribed_at"])]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REWRITTEN = "rewritten", "Rewritten"
        PENDING_REVIEW = "pending_review", "Pending Review"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    original_title = models.CharField(max_length=300)
    original_content = models.TextField()
    rewritten_title = models.CharField(max_length=300, blank=True)
    rewritten_content = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    source_name = models.CharField(max_length=120)
    source_url = models.URLField(max_length=500, unique=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    image_url = models.URLField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="articles")
    categories = models.ManyToManyField(Category, blank=True, related_name="categorized_articles")
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_article_slug(self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)
        if (
            self.status == self.Status.PUBLISHED
            and self.category_id
            and not self.categories.exists()
        ):
            self.categories.add(self.category)

    def __str__(self) -> str:
        return self.title


class ArticleSlugRedirect(models.Model):
    old_slug = models.SlugField(max_length=320, unique=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="slug_redirects")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.old_slug} -> {self.article.slug}"
