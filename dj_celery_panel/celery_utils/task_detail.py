from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface


@dataclass(frozen=True)
class TaskDetailPage:
    task: Optional[dict]
    error: Optional[str] = None


class CeleryTaskInstanceDetailInterface(CeleryAbstractInterface):
    """
    Utility class that powers the task detail view.

    Similar to the task list interface, there are many ways to generate a task detail
    view and this class provides a unified interface for all these approaches.
    """

    BACKEND_KEY = "task_detail_backend"
    DEFAULT_BACKEND = (
        "dj_celery_panel.celery_utils.CeleryTaskDetailDjangoCeleryResultsBackend"
    )

    def get_task_detail(self, task_id: str) -> TaskDetailPage:
        return self.backend.get_task_detail(task_id)


class CeleryTaskDetailDjangoCeleryResultsBackend:
    """Backend for retrieving task details from django-celery-results."""

    def __init__(self, app):
        self.app = app

    def get_task_detail(self, task_id: str) -> TaskDetailPage:
        """Get task details from django-celery-results database."""
        try:
            from django_celery_results.models import TaskResult

            task = TaskResult.objects.filter(task_id=task_id).first()

            if not task:
                return TaskDetailPage(task=None, error="Task not found")

            # Format task details
            task_detail = {
                "id": task.task_id,
                "name": task.task_name,
                "status": task.status,
                "result": task.result,
                "date_created": task.date_created,
                "date_done": task.date_done,
                "date_started": getattr(task, "date_started", None),
                "worker": task.worker,
                "args": task.task_args,
                "kwargs": task.task_kwargs,
                "traceback": task.traceback if hasattr(task, "traceback") else None,
                "meta": task.meta if hasattr(task, "meta") else None,
            }

            # Calculate duration if both dates are available
            if task.date_done and task.date_created:
                duration = task.date_done - task.date_created
                task_detail["duration"] = duration.total_seconds()
            else:
                task_detail["duration"] = None

            return TaskDetailPage(task=task_detail)

        except ImportError:
            return TaskDetailPage(
                task=None, error="django-celery-results not installed"
            )
        except Exception as e:
            return TaskDetailPage(task=None, error=str(e))
