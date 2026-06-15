from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify
from unidecode import unidecode


MAX_LENGTH = 280


def slug_base(title: str) -> str:
    return slugify(unidecode(str(title or "")))[:MAX_LENGTH] or "news-story"


def clean_article_slugs(apps, schema_editor):
    Article = apps.get_model("news", "Article")
    ArticleSlugRedirect = apps.get_model("news", "ArticleSlugRedirect")
    articles = list(Article.objects.all().order_by("created_at", "id"))
    old_slug_owners = {article.slug: article.id for article in articles}
    assigned: set[str] = set()
    desired_slugs: dict[int, str] = {}

    articles.sort(
        key=lambda article: (
            article.slug != slug_base(article.title),
            article.created_at,
            article.id,
        )
    )

    for article in articles:
        base = slug_base(article.title)
        candidate = base
        counter = 2
        while candidate in assigned or (
            candidate in old_slug_owners and old_slug_owners[candidate] != article.id
        ):
            suffix = f"-{counter}"
            candidate = f"{base[: MAX_LENGTH - len(suffix)]}{suffix}"
            counter += 1
        assigned.add(candidate)
        desired_slugs[article.id] = candidate

    changed = [article for article in articles if article.slug != desired_slugs[article.id]]
    for article in changed:
        ArticleSlugRedirect.objects.get_or_create(
            old_slug=article.slug,
            defaults={"article_id": article.id},
        )
        article.slug = f"slug-migration-{article.id}"
        article.save(update_fields=["slug"])

    for article in changed:
        article.slug = desired_slugs[article.id]
        article.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0003_author_article_author"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticleSlugRedirect",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("old_slug", models.SlugField(max_length=320, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="slug_redirects",
                        to="news.article",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.RunPython(clean_article_slugs, migrations.RunPython.noop),
    ]
