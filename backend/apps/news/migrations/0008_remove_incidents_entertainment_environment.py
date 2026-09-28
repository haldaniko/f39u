from django.db import migrations


CATEGORY_REPLACEMENTS = {
    "incidents": "world",
    "entertainment": "culture",
    "environment": "science",
}


def remove_categories(apps, schema_editor):
    Article = apps.get_model("news", "Article")
    Category = apps.get_model("news", "Category")

    for old_slug, replacement_slug in CATEGORY_REPLACEMENTS.items():
        old_category = Category.objects.filter(slug=old_slug).first()
        replacement = Category.objects.filter(slug=replacement_slug).first()
        if old_category is None:
            continue

        if replacement is not None:
            Article.objects.filter(category=old_category).update(category=replacement)
            for article in old_category.categorized_articles.all():
                article.categories.add(replacement)

        old_category.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0007_rename_economy_finance_to_finance"),
    ]

    operations = [
        migrations.RunPython(remove_categories, migrations.RunPython.noop),
    ]
