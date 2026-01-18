"""
Tests for the configuration page.
"""

from django.urls import reverse

from .base import CeleryPanelTestCase


class TestConfigurationPage(CeleryPanelTestCase):
    """Test cases for the configuration page."""

    def test_configuration_page_loads(self):
        """Test that the configuration page loads successfully."""
        response = self.client.get(reverse("dj_celery_panel:configuration"))
        
        self.assertEqual(response.status_code, 200)

    def test_configuration_shows_panel_settings(self):
        """Test that the configuration page shows DJ Celery Panel settings."""
        response = self.client.get(reverse("dj_celery_panel:configuration"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DJ Celery Panel Settings")
        self.assertContains(response, "Backend Configuration")

    def test_configuration_shows_celery_settings(self):
        """Test that the configuration page shows Celery settings."""
        response = self.client.get(reverse("dj_celery_panel:configuration"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celery Settings")
        self.assertContains(response, "Connection & Serialization")

    def test_configuration_shows_task_execution_settings(self):
        """Test that the configuration page shows task execution settings."""
        response = self.client.get(reverse("dj_celery_panel:configuration"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task Execution")

    def test_configuration_shows_queue_routing_settings(self):
        """Test that the configuration page shows queue and routing settings."""
        response = self.client.get(reverse("dj_celery_panel:configuration"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Queue & Routing")

    def test_configuration_shows_worker_settings(self):
        """Test that the configuration page shows worker settings."""
        response = self.client.get(reverse("dj_celery_panel:configuration"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Worker Settings")

    def test_configuration_requires_authentication(self):
        """Test that unauthenticated users cannot access the configuration page."""
        from django.test import Client
        
        client = Client()
        response = client.get(reverse("dj_celery_panel:configuration"))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_configuration_requires_staff_permission(self):
        """Test that non-staff users cannot access the configuration page."""
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(
            username="regular_user", password="testpass123", is_staff=False
        )
        
        client = Client()
        client.force_login(user)
        response = client.get(reverse("dj_celery_panel:configuration"))
        
        # Should redirect to admin login
        self.assertEqual(response.status_code, 302)
