from __future__ import annotations

from django.db import models
from django.utils.text import slugify


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
            self.slug = slugify(self.title)[:280]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
