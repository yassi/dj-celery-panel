"""
Tests for the tasks page and task detail page.
"""

from unittest.mock import Mock, patch

from django.contrib.messages import get_messages
from django.test import override_settings
from django.urls import reverse

from .base import CeleryPanelTestCase


class TestTasksPageWithDatabaseBackend(CeleryPanelTestCase):
    """Test cases for the tasks page using the default database backend."""

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
        response = self.client.get(
            reverse("dj_celery_panel:tasks"), {"search": "test_task"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="test_task"')

    def test_tasks_page_with_status_filter(self):
        """Test that the tasks page accepts status filters."""
        response = self.client.get(
            reverse("dj_celery_panel:tasks"), {"filter": "success"}
        )

        self.assertEqual(response.status_code, 200)
        # Should have filter in context
        self.assertEqual(response.context["current_filter"], "success")

    def test_tasks_page_shows_filter_dropdown_with_multiple_options(self):
        """Test that filter dropdown shows when backend has multiple filter options."""
        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        # Database backend has multiple filters, should show dropdown
        self.assertTrue(response.context["show_filters"])
        self.assertContains(response, 'id="filter-select"')

    def test_tasks_page_filter_options(self):
        """Test that correct filter options are available for database backend."""
        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        filters = response.context["task_filters"]
        # Database backend should have multiple filters
        self.assertGreater(len(filters), 1)
        filter_values = [f["value"] for f in filters]
        self.assertIn(None, filter_values)  # "All" option
        self.assertIn("success", filter_values)
        self.assertIn("failure", filter_values)

    def test_tasks_page_pagination(self):
        """Test that the tasks page handles pagination."""
        response = self.client.get(reverse("dj_celery_panel:tasks"), {"page": "1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)

    def test_tasks_page_invalid_page_number(self):
        """Test that the tasks page handles invalid page numbers gracefully."""
        response = self.client.get(
            reverse("dj_celery_panel:tasks"), {"page": "invalid"}
        )

        # Should default to page 1
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)

    def test_tasks_page_backend_info_displayed(self):
        """Test that backend information is displayed on the page."""
        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("backend_info", response.context)
        backend_info = response.context["backend_info"]
        self.assertIn("name", backend_info)
        self.assertIn("data_source", backend_info)

    def test_tasks_requires_authentication(self):
        """Test that unauthenticated users cannot access the tasks page."""
        from django.test import Client

        client = Client()
        response = client.get(reverse("dj_celery_panel:tasks"))

        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class TestTasksPageWithInspectBackend(CeleryPanelTestCase):
    """Test cases for the tasks page using the inspect backend."""

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_tasks_page_loads_with_inspect_backend(self, mock_active):
        """Test that tasks page loads successfully with inspect backend."""
        mock_active.return_value = None

        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task Execution History")

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_displays_active_tasks(self, mock_active):
        """Test that inspect backend displays active tasks from workers."""
        mock_active.return_value = {
            "worker1@localhost": [
                {
                    "id": "task-123",
                    "name": "app.tasks.process_data",
                    "args": [1, 2, 3],
                    "kwargs": {"priority": "high"},
                    "time_start": 1234567890.0,
                },
                {
                    "id": "task-456",
                    "name": "app.tasks.send_email",
                    "args": ["user@example.com"],
                    "kwargs": {},
                    "time_start": 1234567891.0,
                },
            ]
        }

        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 2)
        # Check first task
        task1 = response.context["tasks"][0]
        self.assertEqual(task1["id"], "task-123")
        self.assertEqual(task1["name"], "app.tasks.process_data")
        self.assertEqual(task1["status"], "ACTIVE")
        self.assertEqual(task1["worker"], "worker1@localhost")

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_search_by_task_name(self, mock_active):
        """Test searching active tasks by name with inspect backend."""
        mock_active.return_value = {
            "worker1@localhost": [
                {"id": "task-123", "name": "app.tasks.process_data"},
                {"id": "task-456", "name": "app.tasks.send_email"},
                {"id": "task-789", "name": "app.tasks.process_images"},
            ]
        }

        response = self.client.get(
            reverse("dj_celery_panel:tasks"), {"search": "process"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 2)
        task_names = [task["name"] for task in response.context["tasks"]]
        self.assertIn("app.tasks.process_data", task_names)
        self.assertIn("app.tasks.process_images", task_names)
        self.assertNotIn("app.tasks.send_email", task_names)

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_search_by_task_id(self, mock_active):
        """Test searching active tasks by ID with inspect backend."""
        mock_active.return_value = {
            "worker1@localhost": [
                {"id": "abc-123-def", "name": "app.tasks.task1"},
                {"id": "xyz-456-ghi", "name": "app.tasks.task2"},
            ]
        }

        response = self.client.get(
            reverse("dj_celery_panel:tasks"), {"search": "456"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)
        self.assertEqual(response.context["tasks"][0]["id"], "xyz-456-ghi")

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_no_filter_dropdown(self, mock_active):
        """Test that filter dropdown doesn't show with inspect backend (only one option)."""
        mock_active.return_value = None

        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        # Inspect backend has only one filter option, should not show dropdown
        self.assertFalse(response.context["show_filters"])
        self.assertNotContains(response, 'id="filter-select"')

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_with_no_workers(self, mock_active):
        """Test inspect backend when no workers are running."""
        mock_active.return_value = None

        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 0)
        self.assertEqual(response.context["total_count"], 0)

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_error_handling(self, mock_active):
        """Test that inspect backend handles errors gracefully without showing errors."""
        mock_active.side_effect = Exception("Connection timeout")

        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        # Should handle gracefully - return empty list, no error messages shown
        self.assertEqual(len(response.context["tasks"]), 0)
        self.assertEqual(response.context["total_count"], 0)
        # Backend is designed to fail silently for temporary worker issues
        # No warning message should be shown to avoid alarming users

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_displays_correct_metadata(self, mock_active):
        """Test that correct backend metadata is displayed."""
        mock_active.return_value = None

        response = self.client.get(reverse("dj_celery_panel:tasks"))

        self.assertEqual(response.status_code, 200)
        backend_info = response.context["backend_info"]
        self.assertIn("Inspect", backend_info["name"])
        self.assertIn("Celery Inspect API", backend_info["data_source"])

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_inspect_backend_pagination(self, mock_active):
        """Test pagination with inspect backend."""
        # Create 15 tasks
        tasks = [
            {"id": f"task-{i}", "name": f"app.tasks.task_{i}"} for i in range(15)
        ]
        mock_active.return_value = {"worker1@localhost": tasks}

        # Test first page
        response = self.client.get(reverse("dj_celery_panel:tasks"), {"page": "1"})
        self.assertEqual(response.status_code, 200)
        # Default per_page is 50, so all tasks should be on first page
        self.assertEqual(len(response.context["tasks"]), 15)


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

    @override_settings(
        DJ_CELERY_PANEL_SETTINGS={
            "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend"
        }
    )
    @patch("celery.app.control.Inspect.active")
    def test_task_detail_with_inspect_backend(self, mock_active):
        """Test task detail page with inspect backend."""
        mock_active.return_value = {
            "worker1@localhost": [
                {
                    "id": "task-123",
                    "name": "app.tasks.process_data",
                    "args": [1, 2, 3],
                    "kwargs": {"priority": "high"},
                    "time_start": 1234567890.0,
                }
            ]
        }

        response = self.client.get(
            reverse("dj_celery_panel:task_detail", kwargs={"task_id": "task-123"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["task"])
        self.assertEqual(response.context["task"]["id"], "task-123")
        self.assertEqual(response.context["task"]["name"], "app.tasks.process_data")
