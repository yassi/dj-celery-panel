from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface


@dataclass(frozen=True)
class TaskListPage:
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


class CeleryTaskListInterface(CeleryAbstractInterface):
    """
    Utility class that powers the task list search engine.
    """

    BACKEND_KEY = "task_backend"
    DEFAULT_BACKEND = (
        "dj_celery_panel.celery_utils.CeleryTaskListDjangoCeleryResultsBackend"
    )

    def get_tasks(self, search_query=None, page=1, per_page=50) -> TaskListPage:
        return self.backend.get_tasks(
            search_query=search_query, page=page, per_page=per_page
        )


class CeleryTaskListDjangoCeleryResultsBackend:
    """
    Utility class that powers the task list search engine.

    There are many ways to generate a task list
    - using the celery inspect api for direct queries to workers (slow)
    - querying a result backend directly (django-celery-results)
    - using a more custom approach where we save worker events and then query them

    This class provides a unified interface for all these approaches. The view layer
    should not need to know about the underlying implementation details and should be
    able to use the same interface for all three approaches.
    """

    def __init__(self, app):
        """
        Initialize the task list interface.

        Args:
            app: Celery application instance
            mode: str - 'django-celery-results', 'inspect', or 'monitor'
        """
        self.app = app

    def get_tasks(self, search_query=None, page=1, per_page=50) -> TaskListPage:
        """Get tasks from django-celery-results database."""
        try:
            from django_celery_results.models import TaskResult
            from django.core.paginator import Paginator

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
