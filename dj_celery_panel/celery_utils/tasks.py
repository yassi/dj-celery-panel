from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface


@dataclass(frozen=True)
class TaskListPage:
    """Return type for task list queries."""

    tasks: list[dict]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    has_previous: bool = False
    has_next: bool = False
    previous_page: Optional[int] = None
    next_page: Optional[int] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class TaskDetailPage:
    """Return type for single task detail queries."""

    task: Optional[dict]
    error: Optional[str] = None


class CeleryTasksInterface(CeleryAbstractInterface):
    """
    Interface for retrieving task information (both lists and individual tasks).
    """

    BACKEND_KEY = "tasks_backend"
    DEFAULT_BACKEND = (
        "dj_celery_panel.celery_utils.CeleryTasksDjangoCeleryResultsBackend"
    )

    def get_tasks(self, search_query=None, page=1, per_page=50) -> TaskListPage:
        """Get a paginated list of tasks with optional search filtering."""
        return self.backend.get_tasks(
            search_query=search_query, page=page, per_page=per_page
        )

    def get_task_detail(self, task_id: str) -> TaskDetailPage:
        """Get detailed information about a single task."""
        return self.backend.get_task_detail(task_id)


class CeleryTasksDjangoCeleryResultsBackend:
    """
    Backend for retrieving task information from django-celery-results.

    This backend provides both list and detail views by querying the
    django-celery-results database directly.
    """

    def __init__(self, app):
        """
        Initialize the tasks backend.

        Args:
            app: Celery application instance
        """
        self.app = app

    def get_tasks(self, search_query=None, page=1, per_page=50) -> TaskListPage:
        """Get tasks from django-celery-results database."""
        try:
            from django.core.paginator import Paginator
            from django_celery_results.models import TaskResult

            # Base queryset
            queryset = TaskResult.objects.all()

            # Apply search filter
            if search_query:
                queryset = queryset.filter(task_name__icontains=search_query)

            # Order by most recent first
            queryset = queryset.order_by("-date_created")

            # Paginate
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)

            # Format tasks
            tasks = []
            for task in page_obj:
                tasks.append(
                    {
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
                    }
                )

            return TaskListPage(
                tasks=tasks,
                total_count=paginator.count,
                page=page_obj.number,
                per_page=per_page,
                total_pages=paginator.num_pages,
                has_previous=page_obj.has_previous(),
                has_next=page_obj.has_next(),
                previous_page=(
                    page_obj.previous_page_number() if page_obj.has_previous() else None
                ),
                next_page=(
                    page_obj.next_page_number() if page_obj.has_next() else None
                ),
            )

        except ImportError:
            return TaskListPage(
                tasks=[],
                total_count=0,
                page=page,
                per_page=per_page,
                total_pages=0,
                error="django-celery-results not installed",
            )
        except Exception as e:
            return TaskListPage(
                tasks=[],
                total_count=0,
                page=page,
                per_page=per_page,
                total_pages=0,
                error=str(e),
            )

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
