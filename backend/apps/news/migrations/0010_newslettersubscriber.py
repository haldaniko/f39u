from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0009_author_photo"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsletterSubscriber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "source",
                    models.CharField(
                        choices=[("footer", "Footer"), ("popup", "Popup")],
                        default="footer",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("subscribed_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-subscribed_at"],
            },
        ),
        migrations.AddIndex(
            model_name="newslettersubscriber",
            index=models.Index(fields=["is_active", "subscribed_at"], name="news_newsle_is_acti_5fcd22_idx"),
        ),
    ]
