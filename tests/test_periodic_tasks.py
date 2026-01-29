"""
Tests for the Celery Panel periodic tasks interface.
"""

from datetime import datetime, timezone
from unittest.mock import patch

from celery import Celery
from celery.schedules import crontab
from django.test import TestCase
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
)

from dj_celery_panel.celery_utils import (
    CeleryPeriodicTasksConfigBackend,
    CeleryPeriodicTasksDjangoCeleryBeatBackend,
    CeleryPeriodicTasksInterface,
)


class TestPeriodicTasksConfigBackend(TestCase):
    """Test cases for the config-based periodic tasks backend."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = Celery("test_app")
        self.app.conf.beat_schedule = {
            "test-task": {
                "task": "app.tasks.test_task",
                "schedule": crontab(minute="*/5"),
                "args": [1, 2],
                "kwargs": {"key": "value"},
            },
            "another-task": {
                "task": "app.tasks.another_task",
                "schedule": crontab(hour="0", minute="0"),
            },
        }

    def test_get_periodic_tasks_from_beat_schedule(self):
        """Test retrieving periodic tasks from beat_schedule configuration."""
        backend = CeleryPeriodicTasksConfigBackend(self.app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 2)
        self.assertEqual(result.periodic_tasks_count, 2)
        self.assertIsNone(result.error)

        # Check first task
        task1 = result.periodic_tasks[0]
        self.assertEqual(task1["name"], "test-task")
        self.assertEqual(task1["task"], "app.tasks.test_task")
        self.assertEqual(task1["args"], [1, 2])
        self.assertEqual(task1["kwargs"], {"key": "value"})

        # Check second task
        task2 = result.periodic_tasks[1]
        self.assertEqual(task2["name"], "another-task")
        self.assertEqual(task2["task"], "app.tasks.another_task")

    def test_get_periodic_tasks_empty_schedule(self):
        """Test retrieving periodic tasks when beat_schedule is empty."""
        self.app.conf.beat_schedule = {}
        backend = CeleryPeriodicTasksConfigBackend(self.app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 0)
        self.assertEqual(result.periodic_tasks_count, 0)
        self.assertIsNone(result.error)

    def test_get_periodic_tasks_no_beat_schedule(self):
        """Test retrieving periodic tasks when beat_schedule doesn't exist."""
        app = Celery("test_app_no_beat")
        backend = CeleryPeriodicTasksConfigBackend(app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 0)
        self.assertEqual(result.periodic_tasks_count, 0)
        self.assertIsNone(result.error)

    def test_backend_metadata(self):
        """Test backend metadata attributes."""
        backend = CeleryPeriodicTasksConfigBackend(self.app)
        self.assertEqual(
            backend.BACKEND_DESCRIPTION,
            "Periodic tasks from beat_schedule configuration",
        )
        self.assertEqual(backend.DATA_SOURCE, "Celery Configuration (beat_schedule)")


class TestPeriodicTasksDjangoCeleryBeatBackend(TestCase):
    """Test cases for the django-celery-beat periodic tasks backend."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = Celery("test_app")
        
        # Create interval schedule (every 5 minutes)
        self.interval_schedule = IntervalSchedule.objects.create(
            every=5,
            period=IntervalSchedule.MINUTES,
        )
        
        # Create crontab schedule (midnight daily)
        self.crontab_schedule = CrontabSchedule.objects.create(
            minute="0",
            hour="0",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()

    def test_get_periodic_tasks_from_database(self):
        """Test retrieving periodic tasks from django-celery-beat database."""
        # Create a periodic task with interval schedule
        task1 = PeriodicTask.objects.create(
            name="db-task-1",
            task="app.tasks.db_task",
            interval=self.interval_schedule,
            enabled=True,
            args='[1, 2]',
            kwargs='{"key": "value"}',
            total_run_count=5,
        )
        
        # Create a periodic task with crontab schedule
        task2 = PeriodicTask.objects.create(
            name="db-task-2",
            task="app.tasks.another_db_task",
            crontab=self.crontab_schedule,
            enabled=True,
            args="[]",
            kwargs="{}",
            total_run_count=10,
        )

        backend = CeleryPeriodicTasksDjangoCeleryBeatBackend(self.app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 2)
        self.assertEqual(result.periodic_tasks_count, 2)
        self.assertIsNone(result.error)

        # Check first task (interval)
        periodic_task1 = result.periodic_tasks[0]
        self.assertEqual(periodic_task1["name"], "db-task-1")
        self.assertEqual(periodic_task1["task"], "app.tasks.db_task")
        self.assertEqual(periodic_task1["args"], [1, 2])
        self.assertEqual(periodic_task1["kwargs"], {"key": "value"})
        self.assertIn("5 minute", periodic_task1["schedule"].lower())
        self.assertEqual(periodic_task1["total_run_count"], 5)
        self.assertTrue(periodic_task1["enabled"])

        # Check second task (crontab)
        periodic_task2 = result.periodic_tasks[1]
        self.assertEqual(periodic_task2["name"], "db-task-2")
        self.assertEqual(periodic_task2["task"], "app.tasks.another_db_task")
        self.assertEqual(periodic_task2["args"], [])
        self.assertEqual(periodic_task2["kwargs"], {})
        self.assertIn("0 0", periodic_task2["schedule"])
        self.assertEqual(periodic_task2["total_run_count"], 10)
        self.assertTrue(periodic_task2["enabled"])

    def test_get_periodic_tasks_only_enabled(self):
        """Test that only enabled periodic tasks are returned."""
        # Create enabled task
        PeriodicTask.objects.create(
            name="enabled-task",
            task="app.tasks.enabled_task",
            interval=self.interval_schedule,
            enabled=True,
        )
        
        # Create disabled task
        PeriodicTask.objects.create(
            name="disabled-task",
            task="app.tasks.disabled_task",
            interval=self.interval_schedule,
            enabled=False,
        )

        backend = CeleryPeriodicTasksDjangoCeleryBeatBackend(self.app)
        result = backend.get_periodic_tasks()

        # Should only return the enabled task
        self.assertEqual(len(result.periodic_tasks), 1)
        self.assertEqual(result.periodic_tasks[0]["name"], "enabled-task")

    def test_get_periodic_tasks_with_last_run_at(self):
        """Test that last_run_at is included in the result."""
        last_run = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        PeriodicTask.objects.create(
            name="task-with-history",
            task="app.tasks.historical_task",
            interval=self.interval_schedule,
            enabled=True,
            last_run_at=last_run,
            total_run_count=42,
        )

        backend = CeleryPeriodicTasksDjangoCeleryBeatBackend(self.app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 1)
        task = result.periodic_tasks[0]
        self.assertEqual(task["last_run_at"], last_run)
        self.assertEqual(task["total_run_count"], 42)

    def test_get_periodic_tasks_empty_database(self):
        """Test retrieving periodic tasks when database is empty."""
        backend = CeleryPeriodicTasksDjangoCeleryBeatBackend(self.app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 0)
        self.assertEqual(result.periodic_tasks_count, 0)
        self.assertIsNone(result.error)

    def test_get_periodic_tasks_with_invalid_json(self):
        """Test handling of invalid JSON in args/kwargs."""
        PeriodicTask.objects.create(
            name="task-with-invalid-json",
            task="app.tasks.invalid_task",
            interval=self.interval_schedule,
            enabled=True,
            args="not valid json",
            kwargs="also not valid",
        )

        backend = CeleryPeriodicTasksDjangoCeleryBeatBackend(self.app)
        result = backend.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 1)
        # Should fallback to empty args/kwargs on JSON error
        task = result.periodic_tasks[0]
        self.assertEqual(task["args"], [])
        self.assertEqual(task["kwargs"], {})

    def test_backend_metadata(self):
        """Test backend metadata attributes."""
        backend = CeleryPeriodicTasksDjangoCeleryBeatBackend(self.app)
        self.assertEqual(
            backend.BACKEND_DESCRIPTION,
            "Periodic tasks from django-celery-beat database",
        )
        self.assertEqual(
            backend.DATA_SOURCE, "Django Database (django-celery-beat)"
        )


class TestPeriodicTasksInterface(TestCase):
    """Test cases for the periodic tasks interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = Celery("test_app")
        self.app.conf.beat_schedule = {
            "test-task": {
                "task": "app.tasks.test_task",
                "schedule": crontab(minute="*/5"),
            },
        }

    def test_interface_uses_default_backend(self):
        """Test that interface uses the default config backend."""
        interface = CeleryPeriodicTasksInterface(self.app)
        result = interface.get_periodic_tasks()

        self.assertEqual(len(result.periodic_tasks), 1)
        self.assertIsInstance(
            interface.backend, CeleryPeriodicTasksConfigBackend
        )

    def test_interface_can_override_backend(self):
        """Test that interface can override backend via settings."""
        backend_path = (
            "dj_celery_panel.celery_utils.CeleryPeriodicTasksDjangoCeleryBeatBackend"
        )
        interface = CeleryPeriodicTasksInterface(self.app, backend_path=backend_path)

        self.assertIsInstance(
            interface.backend, CeleryPeriodicTasksDjangoCeleryBeatBackend
        )

    def test_interface_get_backend_info(self):
        """Test getting backend information from interface."""
        interface = CeleryPeriodicTasksInterface(self.app)
        backend_info = interface.get_backend_info()

        self.assertIn("name", backend_info)
        self.assertIn("module", backend_info)
        self.assertIn("description", backend_info)
        self.assertIn("data_source", backend_info)
        self.assertEqual(backend_info["name"], "CeleryPeriodicTasksConfigBackend")
