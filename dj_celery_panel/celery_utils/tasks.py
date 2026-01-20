from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector


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

    def get_tasks(
        self, search_query=None, page=1, per_page=50, filter_type=None
    ) -> TaskListPage:
        """Get a paginated list of tasks with optional search filtering and type filtering."""
        # If no filter specified, use the backend's default filter
        if filter_type is None:
            filter_type = getattr(self.backend, "DEFAULT_FILTER", None)

        return self.backend.get_tasks(
            search_query=search_query,
            page=page,
            per_page=per_page,
            filter_type=filter_type,
        )

    def get_task_detail(self, task_id: str) -> TaskDetailPage:
        """Get detailed information about a single task."""
        return self.backend.get_task_detail(task_id)

    def get_available_filters(self):
        """Get available filter options from the backend."""
        return getattr(self.backend, "AVAILABLE_FILTERS", [])

    def get_default_filter(self):
        """Get the default filter from the backend."""
        return getattr(self.backend, "DEFAULT_FILTER", None)


class CeleryTasksDjangoCeleryResultsBackend:
    """
    Backend for retrieving task information from django-celery-results.

    This backend provides both list and detail views by querying the
    django-celery-results database directly.
    """

    BACKEND_DESCRIPTION = "Task history with pagination and search"
    DATA_SOURCE = "Django Database (django-celery-results)"
    DEFAULT_FILTER = None  # Show all tasks by default
    AVAILABLE_FILTERS = [
        {"value": None, "label": "All"},
        {"value": "pending", "label": "Pending"},
        {"value": "started", "label": "Started"},
        {"value": "success", "label": "Success"},
        {"value": "failure", "label": "Failure"},
    ]

    def __init__(self, app):
        """
        Initialize the tasks backend.

        Args:
            app: Celery application instance
        """
        self.app = app

    def get_tasks(
        self, search_query=None, page=1, per_page=50, filter_type=None
    ) -> TaskListPage:
        """Get tasks from django-celery-results database."""
        try:
            from django.core.paginator import Paginator
            from django.db.models import Q
            from django_celery_results.models import TaskResult

            # Base queryset
            queryset = TaskResult.objects.all()

            # Apply search filter (search by both task name and task ID)
            if search_query:
                queryset = queryset.filter(
                    Q(task_name__icontains=search_query)
                    | Q(task_id__icontains=search_query)
                )

            # Apply status filter
            if filter_type:
                queryset = queryset.filter(status__iexact=filter_type)

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


class CeleryTasksInspectBackend:
    """
    Backend for retrieving real-time task information from Celery inspect API.

    This backend provides live information about currently executing tasks
    by querying the Celery control/inspect API.
    """

    BACKEND_DESCRIPTION = "Real-time active tasks from workers"
    DATA_SOURCE = "Celery Inspect API (active tasks only)"
    DEFAULT_FILTER = "active"
    AVAILABLE_FILTERS = [
        {"value": "active", "label": "Active"},
    ]

    def __init__(self, app):
        """
        Initialize the tasks inspect backend.

        Args:
            app: Celery application instance
        """
        self.app = app
        self.inspector = CeleryInspector(app)

    def get_tasks(
        self, search_query=None, page=1, per_page=50, filter_type=None
    ) -> TaskListPage:
        """
        Get active tasks from Celery inspect API.

        Args:
            search_query: Optional search query to filter by task name or task ID
            page: Page number for pagination
            per_page: Number of tasks per page
            filter_type: Type of tasks to retrieve (only "active" supported).
                        Should always be provided by the interface using DEFAULT_FILTER.

        Returns:
            TaskListPage with task information
        """
        try:
            all_tasks = []

            # Get active tasks from all workers using CeleryInspector
            try:
                inspect = self.app.control.inspect()
                active_tasks = inspect.active()
                if active_tasks:
                    for worker, tasks in active_tasks.items():
                        for task in tasks:
                            task["worker"] = worker
                            task["state"] = "ACTIVE"
                            all_tasks.append(task)
            except Exception as e:
                # Log but don't fail - workers might be temporarily unavailable
                import logging

                logging.warning(f"Failed to get active tasks: {e}")

            # Apply search filter (search by both task name and task ID)
            if search_query:
                search_lower = search_query.lower()
                all_tasks = [
                    task
                    for task in all_tasks
                    if search_lower in task.get("name", "").lower()
                    or search_lower in task.get("id", "").lower()
                ]

            # Calculate pagination
            total_count = len(all_tasks)
            total_pages = (total_count + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_tasks = all_tasks[start_idx:end_idx]

            # Format tasks
            formatted_tasks = []
            for task in paginated_tasks:
                formatted_task = {
                    "id": task.get("id", "N/A"),
                    "name": task.get("name", "Unknown"),
                    "status": task.get("state", "UNKNOWN"),
                    "worker": task.get("worker"),
                    "args": task.get("args"),
                    "kwargs": task.get("kwargs"),
                    "date_created": None,  # Not available in inspect API
                    "date_done": None,
                    "date_started": None,
                    "result": None,
                }

                # Add ETA for scheduled tasks
                if "eta" in task:
                    formatted_task["eta"] = task["eta"]

                # Add time_start for active tasks
                if "time_start" in task:
                    formatted_task["time_start"] = task["time_start"]

                formatted_tasks.append(formatted_task)

            return TaskListPage(
                tasks=formatted_tasks,
                total_count=total_count,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                has_previous=page > 1,
                has_next=page < total_pages,
                previous_page=page - 1 if page > 1 else None,
                next_page=page + 1 if page < total_pages else None,
            )

        except Exception as e:
            import logging

            logging.error(
                f"Error in CeleryTasksInspectBackend.get_tasks: {str(e)}", exc_info=True
            )
            return TaskListPage(
                tasks=[],
                total_count=0,
                page=page,
                per_page=per_page,
                total_pages=0,
                error=f"Error querying inspect API: {str(e)}. Make sure workers are running and reachable.",
            )

    def get_task_detail(self, task_id: str) -> TaskDetailPage:
        """
        Get task details from Celery inspect API.

        Note: The inspect API doesn't provide individual task lookups,
        so we search through active tasks to find a match.
        """
        try:
            # Use CeleryInspector to get active tasks
            inspect = self.app.control.inspect()

            # Search through active tasks
            active_tasks = inspect.active()
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        if task.get("id") == task_id:
                            task["worker"] = worker
                            task["state"] = "ACTIVE"
                            return TaskDetailPage(task=self._format_task_detail(task))

            return TaskDetailPage(
                task=None,
                error="Task not found in active tasks. It may have completed or not yet started.",
            )

        except Exception as e:
            return TaskDetailPage(task=None, error=str(e))

    def _format_task_detail(self, task):
        """Format task data for detail view."""
        formatted = {
            "id": task.get("id", "N/A"),
            "name": task.get("name", "Unknown"),
            "status": task.get("state", "UNKNOWN"),
            "worker": task.get("worker"),
            "args": task.get("args"),
            "kwargs": task.get("kwargs"),
            "date_created": None,
            "date_done": None,
            "date_started": task.get("time_start"),
            "result": None,
            "traceback": None,
            "meta": {},
        }

        # Add additional fields
        if "eta" in task:
            formatted["eta"] = task["eta"]
        if "hostname" in task:
            formatted["hostname"] = task["hostname"]
        if "delivery_info" in task:
            formatted["delivery_info"] = task["delivery_info"]

        return formatted
