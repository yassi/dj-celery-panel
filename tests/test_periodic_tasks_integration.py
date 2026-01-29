"""
Integration tests for periodic tasks in the index view.
"""

from celery import Celery
from celery.schedules import crontab
from django.test import override_settings
from django.urls import reverse

from .base import CeleryPanelTestCase


class TestPeriodicTasksIntegration(CeleryPanelTestCase):
    """Integration tests for periodic tasks display on index page."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Create a test Celery app with beat schedule
        self.test_app = Celery("test_app")
        self.test_app.conf.beat_schedule = {
            "test-periodic-task": {
                "task": "app.tasks.test_periodic",
                "schedule": crontab(minute="*/5"),
                "args": [1, 2],
                "kwargs": {"key": "value"},
            },
        }

    def test_index_displays_periodic_tasks_with_config_backend(self):
        """Test that index page displays periodic tasks with config backend."""
        response = self.client.get(reverse("dj_celery_panel:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Periodic Tasks")
        # Should show backend info
        self.assertContains(response, "CeleryPeriodicTasksConfigBackend")

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "periodic_tasks_backend": "dj_celery_panel.celery_utils.CeleryPeriodicTasksConfigBackend",
        }
    )
    def test_index_with_explicit_config_backend_setting(self):
        """Test that explicit config backend setting works."""
        response = self.client.get(reverse("dj_celery_panel:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Periodic Tasks")

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "periodic_tasks_backend": "dj_celery_panel.celery_utils.CeleryPeriodicTasksDjangoCeleryBeatBackend",
        }
    )
    def test_index_with_django_celery_beat_backend_setting(self):
        """Test that django-celery-beat backend setting works (even if not installed)."""
        response = self.client.get(reverse("dj_celery_panel:index"))

        self.assertEqual(response.status_code, 200)
        # Should show warning message since django-celery-beat is likely not installed
        # But the page should still load successfully
        self.assertContains(response, "Periodic Tasks")

    def test_periodic_tasks_count_displayed(self):
        """Test that periodic tasks count is displayed in overview card."""
        response = self.client.get(reverse("dj_celery_panel:index"))

        self.assertEqual(response.status_code, 200)
        # Should have the periodic tasks count value (might be 0 or more)
        self.assertContains(response, "overview-card")
        self.assertContains(response, "Periodic Tasks")

    def test_backend_info_displayed_for_periodic_tasks(self):
        """Test that backend information is displayed for periodic tasks."""
        response = self.client.get(reverse("dj_celery_panel:index"))

        self.assertEqual(response.status_code, 200)
        # Should show backend info section
        self.assertContains(response, "Backend:")
        # Should show the config backend by default
        self.assertContains(response, "Celery Configuration")
