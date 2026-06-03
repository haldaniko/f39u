from django.db import models


class AISetting(models.Model):
    provider = models.CharField(max_length=40, default="openai")
    model = models.CharField(max_length=120, default="gpt-4.1-mini")
    temperature = models.FloatField(default=0.3)
    max_tokens = models.IntegerField(default=1200)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.provider}:{self.model}"
