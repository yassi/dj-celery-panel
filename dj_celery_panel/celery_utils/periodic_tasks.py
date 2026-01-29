from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface


@dataclass(frozen=True)
class PeriodicTaskListPage:
    """Return type for periodic task list queries."""

    periodic_tasks: list[dict]
    periodic_tasks_count: int
    error: Optional[str] = None


class CeleryPeriodicTasksInterface(CeleryAbstractInterface):
    """
    Interface for retrieving periodic task information.
    """

    BACKEND_KEY = "periodic_tasks_backend"
    DEFAULT_BACKEND = (
        "dj_celery_panel.celery_utils.CeleryPeriodicTasksConfigBackend"
    )

    def get_periodic_tasks(self) -> PeriodicTaskListPage:
        """Get a list of all periodic tasks."""
        return self.backend.get_periodic_tasks()


class CeleryPeriodicTasksConfigBackend:
    """
    Backend for retrieving periodic tasks from Celery configuration (beat_schedule).

    This backend reads from the CELERY_BEAT_SCHEDULE configuration setting.
    """

    BACKEND_DESCRIPTION = "Periodic tasks from beat_schedule configuration"
    DATA_SOURCE = "Celery Configuration (beat_schedule)"

    def __init__(self, app):
        self.app = app

    def get_periodic_tasks(self) -> PeriodicTaskListPage:
        """Get periodic tasks from the beat schedule configuration."""
        periodic_tasks = []
        error = None

        try:
            if hasattr(self.app.conf, "beat_schedule"):
                beat_schedule = self.app.conf.beat_schedule or {}
                for task_name, task_config in beat_schedule.items():
                    periodic_tasks.append(
                        {
                            "name": task_name,
                            "task": task_config.get("task", "N/A"),
                            "schedule": str(task_config.get("schedule", "N/A")),
                            "args": task_config.get("args", []),
                            "kwargs": task_config.get("kwargs", {}),
                        }
                    )
        except Exception as e:
            error = f"Error reading beat_schedule: {str(e)}"

        return PeriodicTaskListPage(
            periodic_tasks=periodic_tasks,
            periodic_tasks_count=len(periodic_tasks),
            error=error,
        )


class CeleryPeriodicTasksDjangoCeleryBeatBackend:
    """
    Backend for retrieving periodic tasks from django-celery-beat database.

    This backend reads from the django_celery_beat.models.PeriodicTask model.
    Requires django-celery-beat to be installed and configured.
    """

    BACKEND_DESCRIPTION = "Periodic tasks from django-celery-beat database"
    DATA_SOURCE = "Django Database (django-celery-beat)"

    def __init__(self, app):
        self.app = app

    def get_periodic_tasks(self) -> PeriodicTaskListPage:
        """Get periodic tasks from the django-celery-beat database."""
        periodic_tasks = []
        error = None

        try:
            from django_celery_beat.models import PeriodicTask

            # Query all enabled periodic tasks
            for task in PeriodicTask.objects.filter(enabled=True).select_related(
                "interval", "crontab", "solar"
            ):
                # Determine the schedule string based on which schedule type is set
                schedule_str = "N/A"
                if task.interval:
                    schedule_str = str(task.interval)
                elif task.crontab:
                    schedule_str = str(task.crontab)
                elif task.solar:
                    schedule_str = str(task.solar)
                elif task.clocked:
                    schedule_str = str(task.clocked)

                # Parse args and kwargs (stored as JSON strings)
                import json

                try:
                    args = json.loads(task.args) if task.args else []
                except (json.JSONDecodeError, TypeError):
                    args = []

                try:
                    kwargs = json.loads(task.kwargs) if task.kwargs else {}
                except (json.JSONDecodeError, TypeError):
                    kwargs = {}

                periodic_tasks.append(
                    {
                        "name": task.name,
                        "task": task.task,
                        "schedule": schedule_str,
                        "args": args,
                        "kwargs": kwargs,
                        "enabled": task.enabled,
                        "last_run_at": task.last_run_at,
                        "total_run_count": task.total_run_count,
                    }
                )

        except ImportError:
            error = "django-celery-beat is not installed. Install it with: pip install django-celery-beat"
        except Exception as e:
            error = f"Error reading periodic tasks from database: {str(e)}"

        return PeriodicTaskListPage(
            periodic_tasks=periodic_tasks,
            periodic_tasks_count=len(periodic_tasks),
            error=error,
        )
