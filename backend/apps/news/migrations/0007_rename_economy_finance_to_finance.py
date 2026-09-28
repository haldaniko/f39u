from django.db import migrations


def rename_to_finance(apps, schema_editor):
    Category = apps.get_model("news", "Category")
    old = Category.objects.filter(slug="economy-finance").first()
    finance = Category.objects.filter(slug="finance").first()

    if old is None:
        if finance is not None:
            finance.name = "Finance"
            finance.description = "The economy, markets, banks, inflation, currencies and investing."
            finance.save(update_fields=["name", "description"])
        return

    if finance is not None and finance.pk != old.pk:
        for article in old.articles.all():
            article.category = finance
            article.save(update_fields=["category"])
        for article in old.categorized_articles.all():
            article.categories.add(finance)
        old.delete()
    else:
        finance = old

    finance.name = "Finance"
    finance.slug = "finance"
    finance.description = "The economy, markets, banks, inflation, currencies and investing."
    finance.save(update_fields=["name", "slug", "description"])


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0006_canonical_article_categories"),
    ]

    operations = [
        migrations.RunPython(rename_to_finance, migrations.RunPython.noop),
    ]
