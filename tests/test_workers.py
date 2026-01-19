"""
Tests for the workers page and worker detail page.
"""

from django.urls import reverse

from .base import CeleryPanelTestCase


class TestWorkersPage(CeleryPanelTestCase):
    """Test cases for the workers list page."""

    def test_workers_page_loads(self):
        """Test that the workers page loads successfully."""
        response = self.client.get(reverse("dj_celery_panel:workers"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Workers")

    def test_workers_page_shows_table_headers(self):
        """Test that the workers page shows appropriate table headers."""
        response = self.client.get(reverse("dj_celery_panel:workers"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Worker Name")
        self.assertContains(response, "Status")
        self.assertContains(response, "Pool")
        self.assertContains(response, "Concurrency")

    def test_workers_page_handles_no_workers(self):
        """Test that the workers page handles case when no workers are running."""
        response = self.client.get(reverse("dj_celery_panel:workers"))
        
        # Should still load successfully even with no workers
        self.assertEqual(response.status_code, 200)

    def test_workers_requires_authentication(self):
        """Test that unauthenticated users cannot access the workers page."""
        from django.test import Client
        
        client = Client()
        response = client.get(reverse("dj_celery_panel:workers"))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class TestWorkerDetailPage(CeleryPanelTestCase):
    """Test cases for the worker detail page."""

    def test_worker_detail_page_loads_with_valid_worker_id(self):
        """Test that the worker detail page loads with a worker ID."""
        # Using a dummy worker ID - the page should load even if worker doesn't exist
        response = self.client.get(
            reverse("dj_celery_panel:worker_detail", kwargs={"worker_id": "celery@test-host"})
        )
        
        self.assertEqual(response.status_code, 200)
        # Page should load successfully and show either worker details or not found message
        self.assertTrue(
            "Worker Details" in response.content.decode() or 
            "Worker Not Found" in response.content.decode()
        )

    def test_worker_detail_shows_not_found_for_invalid_worker(self):
        """Test that the worker detail page shows error for invalid worker."""
        response = self.client.get(
            reverse("dj_celery_panel:worker_detail", kwargs={"worker_id": "nonexistent-worker"})
        )
        
        self.assertEqual(response.status_code, 200)
        # Should show indication that worker wasn't found
        self.assertContains(response, "Worker Not Found")

    def test_worker_detail_requires_authentication(self):
        """Test that unauthenticated users cannot access worker detail."""
        from django.test import Client
        
        client = Client()
        response = client.get(
            reverse("dj_celery_panel:worker_detail", kwargs={"worker_id": "celery@test-host"})
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
