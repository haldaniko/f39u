from django.test import TestCase

from .services import AnalyticsService


class AnalyticsServiceTests(TestCase):
    def test_report_generation(self):
        report = AnalyticsService.create_daily_report()
        self.assertIsNotNone(report.id)
