from rest_framework import serializers

from .models import DailyAnalyticsReport


class DailyAnalyticsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAnalyticsReport
        fields = [
            "date",
            "total_articles",
            "published_articles",
            "pending_articles",
            "source_statistics",
            "created_at",
        ]
