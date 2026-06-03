from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.news.models import Article

from .models import DailyAnalyticsReport
from .serializers import DailyAnalyticsReportSerializer


class AdminStatisticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        payload = {
            "total_articles": Article.objects.count(),
            "published_articles": Article.objects.filter(status=Article.Status.PUBLISHED).count(),
            "pending_moderation": Article.objects.filter(status=Article.Status.PENDING_REVIEW).count(),
            "rejected_articles": Article.objects.filter(status=Article.Status.REJECTED).count(),
        }
        return Response(payload)


class DailyReportsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        queryset = DailyAnalyticsReport.objects.order_by("-date")[:30]
        return Response(DailyAnalyticsReportSerializer(queryset, many=True).data)
