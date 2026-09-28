from django.db import migrations, models
from django.utils.text import slugify


CANONICAL_CATEGORIES = [
    ("Politics", "Domestic and international politics, elections, laws and diplomacy."),
    ("World", "Events in other countries, conflicts and international relations."),
    ("Finance", "The economy, markets, banks, inflation, currencies and investing."),
    ("Business", "Companies, deals, startups and industries."),
    ("Technology", "IT, AI, the internet, gadgets, cybersecurity and space."),
    ("Science", "Research, discoveries, medicine and climate."),
    ("Society", "Social issues, education, migration and demographics."),
    ("Incidents", "Accidents, crime, disasters and emergencies."),
    ("Health", "Medicine, diseases, pharmaceuticals and healthcare."),
    ("Culture", "Film, music, literature and art."),
    ("Sport", "Competitions, teams and athletes."),
    ("Entertainment", "Celebrities, show business, games and internet culture."),
    ("Environment", "Climate, pollution, energy and conservation issues."),
]

CATEGORY_ALIASES = {
    "agriculture": "Business",
    "agriculture & foodtech": "Business",
    "agriculture and foodtech": "Business",
    "ai": "Technology",
    "art": "Culture",
    "artificial intelligence": "Technology",
    "biotech & health": "Health",
    "biotech and health": "Health",
    "business": "Business",
    "culture": "Culture",
    "economics": "Finance",
    "economy": "Finance",
    "economy & finance": "Finance",
    "entertainment": "Entertainment",
    "environment": "Environment",
    "feminism": "Society",
    "finance": "Finance",
    "general": "World",
    "health": "Health",
    "incidents": "Incidents",
    "politics": "Politics",
    "rss": "World",
    "science": "Science",
    "sport": "Sport",
    "sports": "Sport",
    "startups": "Business",
    "technology": "Technology",
    "top": "World",
    "world": "World",
}


def normalize_category_name(name):
    value = str(name or "").strip()
    if not value:
        return "World"
    return CATEGORY_ALIASES.get(value.lower(), value if value in {item[0] for item in CANONICAL_CATEGORIES} else "World")


def install_canonical_categories(apps, schema_editor):
    Article = apps.get_model("news", "Article")
    Category = apps.get_model("news", "Category")

    canonical_by_slug = {}
    for name, description in CANONICAL_CATEGORIES:
        slug = slugify(name)
        category = Category.objects.filter(slug=slug).first() or Category.objects.filter(name__iexact=name).first()
        if category is None:
            category = Category.objects.create(name=name, slug=slug, description=description)
        else:
            category.name = name
            category.slug = slug
            category.description = description
            category.save(update_fields=["name", "slug", "description"])
        canonical_by_slug[slug] = category

    allowed_slugs = set(canonical_by_slug)

    for category in list(Category.objects.all()):
        if category.slug in allowed_slugs:
            continue
        target_name = normalize_category_name(category.name)
        target = canonical_by_slug[slugify(target_name)]
        Article.objects.filter(category=category).update(category=target)
        for article in category.categorized_articles.all():
            article.categories.add(target)
        category.delete()

    world = canonical_by_slug["world"]
    for article in Article.objects.all():
        primary = article.category or world
        if article.category_id is None:
            article.category = primary
            article.save(update_fields=["category"])
        if not article.categories.exists():
            article.categories.add(primary)


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0005_remove_rss_references"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="categories",
            field=models.ManyToManyField(blank=True, related_name="categorized_articles", to="news.category"),
        ),
        migrations.RunPython(install_canonical_categories, migrations.RunPython.noop),
    ]
