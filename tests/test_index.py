"""
Tests for the Celery Panel index/overview page.
"""

from django.urls import reverse

from .base import CeleryPanelTestCase


class TestIndexPage(CeleryPanelTestCase):
    """Test cases for the index page."""

    def test_index_page_loads(self):
        """Test that the index page loads successfully."""
        response = self.client.get(reverse("dj_celery_panel:index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Celery Panel")

    def test_index_shows_configuration_section(self):
        """Test that the index page shows configuration information."""
        response = self.client.get(reverse("dj_celery_panel:index"))
        
        self.assertEqual(response.status_code, 200)
        # Should show broker and result backend info
        self.assertContains(response, "Broker")
        self.assertContains(response, "Result Backend")

    def test_index_shows_registered_tasks(self):
        """Test that the index page shows registered tasks."""
        response = self.client.get(reverse("dj_celery_panel:index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registered Tasks")

    def test_index_shows_periodic_tasks(self):
        """Test that the index page shows periodic tasks."""
        response = self.client.get(reverse("dj_celery_panel:index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Periodic Tasks")

    def test_index_requires_authentication(self):
        """Test that unauthenticated users cannot access the index page."""
        from django.test import Client
        
        client = Client()
        response = client.get(reverse("dj_celery_panel:index"))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_index_requires_staff_permission(self):
        """Test that non-staff users cannot access the index page."""
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(
            username="regular_user", password="testpass123", is_staff=False
        )
        
        client = Client()
        client.force_login(user)
        response = client.get(reverse("dj_celery_panel:index"))
        
        # Should redirect to admin login
        self.assertEqual(response.status_code, 302)
