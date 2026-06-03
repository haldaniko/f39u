from django.db import models


class DailyAnalyticsReport(models.Model):
    date = models.DateField(unique=True)
    total_articles = models.IntegerField(default=0)
    published_articles = models.IntegerField(default=0)
    pending_articles = models.IntegerField(default=0)
    source_statistics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.date)
