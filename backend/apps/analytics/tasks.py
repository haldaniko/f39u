from celery import shared_task

from .services import AnalyticsService


@shared_task
def generate_daily_report_task() -> str:
    report = AnalyticsService.create_daily_report()
    return f"Generated analytics report for {report.date}"
