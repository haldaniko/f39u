from django.db import migrations


def remove_feed_label_references(apps, schema_editor):
    Article = apps.get_model("news", "Article")
    Category = apps.get_model("news", "Category")
    Source = apps.get_model("news", "Source")
    Tag = apps.get_model("news", "Tag")

    general_category = Category.objects.filter(slug="general").first() or Category.objects.filter(name__iexact="General").first()

    if general_category is None:
        general_category = Category.objects.create(
            name="General",
            slug="general",
            description="Latest news, reporting and analysis from FXLFM.",
        )

    if general_category.name != "General":
        general_category.name = "General"
        general_category.save(update_fields=["name"])

    unwanted_categories = Category.objects.filter(name__iexact="rss") | Category.objects.filter(slug__iexact="rss")
    for category in unwanted_categories.distinct():
        if category.pk == general_category.pk:
            continue
        Article.objects.filter(category=category).update(category=general_category)
        category.delete()

    unwanted_tags = Tag.objects.filter(name__iexact="rss") | Tag.objects.filter(slug__iexact="rss")
    unwanted_tags.distinct().delete()

    Source.objects.filter(name__iexact="rss").delete()
    Source.objects.filter(provider__iexact="rss").delete()
    Article.objects.filter(source_name__iexact="rss").update(source_name="Web Feed")


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0004_articleslugredirect_clean_article_slugs"),
    ]

    operations = [
        migrations.RunPython(remove_feed_label_references, migrations.RunPython.noop),
    ]
