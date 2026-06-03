from django.urls import path

from .views import AdminStatisticsView, DailyReportsView

urlpatterns = [
    path("admin/statistics/", AdminStatisticsView.as_view(), name="admin-statistics"),
    path("reports/", DailyReportsView.as_view(), name="daily-reports"),
]
