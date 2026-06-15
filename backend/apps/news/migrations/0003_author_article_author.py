import datetime

import django.db.models.deletion
from django.db import migrations, models


AUTHOR_DEFAULTS = {
    "name": "Maria Nicholson",
    "job_title": "Senior News Editor",
    "bio": (
        "Maria Nicholson is a senior news editor covering global affairs, technology, "
        "business and the people shaping the future. She focuses on clear, accessible "
        "reporting that adds context to fast-moving stories and helps readers understand "
        "why the news matters."
    ),
    "photo_url": (
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330"
        "?auto=format&fit=crop&w=800&q=85"
    ),
    "location": "London, United Kingdom",
    "x_url": "https://x.com/marianicholsonnews",
    "linkedin_url": "https://www.linkedin.com/in/maria-nicholson-news/",
    "instagram_url": "https://www.instagram.com/marianicholson.news/",
    "joined_at": datetime.date(2024, 3, 18),
}


def create_default_author(apps, schema_editor):
    Author = apps.get_model("news", "Author")
    Article = apps.get_model("news", "Article")
    author, _ = Author.objects.get_or_create(
        slug="maria-nicholson",
        defaults=AUTHOR_DEFAULTS,
    )
    Article.objects.filter(author__isnull=True).update(author=author)


def remove_default_author(apps, schema_editor):
    Author = apps.get_model("news", "Author")
    Author.objects.filter(slug="maria-nicholson").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0002_alter_article_image_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(blank=True, max_length=140, unique=True)),
                ("job_title", models.CharField(blank=True, max_length=160)),
                ("bio", models.TextField(blank=True)),
                ("photo_url", models.URLField(blank=True, max_length=500)),
                ("location", models.CharField(blank=True, max_length=160)),
                ("x_url", models.URLField(blank=True, max_length=500)),
                ("linkedin_url", models.URLField(blank=True, max_length=500)),
                ("instagram_url", models.URLField(blank=True, max_length=500)),
                ("joined_at", models.DateField(blank=True, null=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="article",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="articles",
                to="news.author",
            ),
        ),
        migrations.RunPython(create_default_author, remove_default_author),
    ]
