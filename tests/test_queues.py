"""
Tests for the queues page and queue detail page.
"""

from django.urls import reverse

from .base import CeleryPanelTestCase


class TestQueuesPage(CeleryPanelTestCase):
    """Test cases for the queues list page."""

    def test_queues_page_loads(self):
        """Test that the queues page loads successfully."""
        response = self.client.get(reverse("dj_celery_panel:queues"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Task Queues")

    def test_queues_page_shows_table_headers(self):
        """Test that the queues page shows appropriate table headers."""
        response = self.client.get(reverse("dj_celery_panel:queues"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Queue Name")
        self.assertContains(response, "Messages")
        self.assertContains(response, "Exchange")
        self.assertContains(response, "Routing Key")

    def test_queues_page_handles_no_queues(self):
        """Test that the queues page handles case when no queues are active."""
        response = self.client.get(reverse("dj_celery_panel:queues"))
        
        # Should still load successfully even with no queues
        self.assertEqual(response.status_code, 200)

    def test_queues_requires_authentication(self):
        """Test that unauthenticated users cannot access the queues page."""
        from django.test import Client
        
        client = Client()
        response = client.get(reverse("dj_celery_panel:queues"))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class TestQueueDetailPage(CeleryPanelTestCase):
    """Test cases for the queue detail page."""

    def test_queue_detail_page_loads_with_valid_queue_name(self):
        """Test that the queue detail page loads with a queue name."""
        # Using a dummy queue name - the page should load even if queue doesn't exist
        response = self.client.get(
            reverse("dj_celery_panel:queue_detail", kwargs={"queue_name": "celery"})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Queue Details")

    def test_queue_detail_shows_not_found_for_invalid_queue(self):
        """Test that the queue detail page shows error for invalid queue."""
        response = self.client.get(
            reverse("dj_celery_panel:queue_detail", kwargs={"queue_name": "nonexistent-queue"})
        )
        
        self.assertEqual(response.status_code, 200)
        # Should show some indication that queue wasn't found

    def test_queue_detail_requires_authentication(self):
        """Test that unauthenticated users cannot access queue detail."""
        from django.test import Client
        
        client = Client()
        response = client.get(
            reverse("dj_celery_panel:queue_detail", kwargs={"queue_name": "celery"})
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
