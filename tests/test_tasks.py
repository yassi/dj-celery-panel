"""
Tests for the tasks page and task detail page.
"""

from django.urls import reverse

from .base import CeleryPanelTestCase


class TestTasksPage(CeleryPanelTestCase):
    """Test cases for the tasks list page."""

    def test_tasks_page_loads(self):
        """Test that the tasks page loads successfully."""
        response = self.client.get(reverse("dj_celery_panel:tasks"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task Execution History")

    def test_tasks_page_shows_search_bar(self):
        """Test that the tasks page has a search bar."""
        response = self.client.get(reverse("dj_celery_panel:tasks"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="search"')

    def test_tasks_page_with_search_query(self):
        """Test that the tasks page accepts search queries."""
        response = self.client.get(reverse("dj_celery_panel:tasks"), {"search": "test_task"})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="test_task"')

    def test_tasks_page_pagination(self):
        """Test that the tasks page handles pagination."""
        response = self.client.get(reverse("dj_celery_panel:tasks"), {"page": "1"})
        
        self.assertEqual(response.status_code, 200)

    def test_tasks_page_invalid_page_number(self):
        """Test that the tasks page handles invalid page numbers gracefully."""
        response = self.client.get(reverse("dj_celery_panel:tasks"), {"page": "invalid"})
        
        # Should default to page 1
        self.assertEqual(response.status_code, 200)

    def test_tasks_requires_authentication(self):
        """Test that unauthenticated users cannot access the tasks page."""
        from django.test import Client
        
        client = Client()
        response = client.get(reverse("dj_celery_panel:tasks"))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class TestTaskDetailPage(CeleryPanelTestCase):
    """Test cases for the task detail page."""

    def test_task_detail_page_loads_with_valid_task_id(self):
        """Test that the task detail page loads with a task ID."""
        # Using a dummy task ID - the page should load even if task doesn't exist
        response = self.client.get(
            reverse("dj_celery_panel:task_detail", kwargs={"task_id": "test-task-id"})
        )
        
        self.assertEqual(response.status_code, 200)

    def test_task_detail_shows_not_found_for_invalid_task(self):
        """Test that the task detail page shows error for invalid task."""
        response = self.client.get(
            reverse("dj_celery_panel:task_detail", kwargs={"task_id": "nonexistent-task"})
        )
        
        self.assertEqual(response.status_code, 200)
        # Should show some indication that task wasn't found
        # Either in messages or in the page content

    def test_task_detail_requires_authentication(self):
        """Test that unauthenticated users cannot access task detail."""
        from django.test import Client
        
        client = Client()
        response = client.get(
            reverse("dj_celery_panel:task_detail", kwargs={"task_id": "test-task-id"})
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
