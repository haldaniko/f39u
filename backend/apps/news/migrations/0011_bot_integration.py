from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0010_newslettersubscriber"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="bot_image",
            field=models.FileField(blank=True, upload_to="article_images/"),
        ),
        migrations.AddField(
            model_name="article",
            name="integration_id",
            field=models.UUIDField(blank=True, editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="article",
            name="integration_payload_hash",
            field=models.CharField(blank=True, editable=False, max_length=64),
        ),
    ]
