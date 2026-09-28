import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0008_remove_incidents_entertainment_environment"),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="photo",
            field=models.FileField(
                blank=True,
                upload_to="authors/",
                validators=[django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
            ),
        ),
    ]
