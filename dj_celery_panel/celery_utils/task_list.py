class CeleryTaskListInterface:
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

    def __init__(self, app, mode="django-celery-results"):
        """
        Initialize the task list interface.

        Args:
            app: Celery application instance
            mode: str - 'django-celery-results', 'inspect', or 'monitor'
        """
        self.app = app
        self.mode = mode

    def get_tasks(self, search_query=None, page=1, per_page=50):
        """
        Get tasks based on the configured mode.

        Args:
            search_query: str - Filter tasks by name (optional)
            page: int - Page number for pagination
            per_page: int - Number of tasks per page

        Returns:
            dict with:
                - tasks: list of task dictionaries
                - total_count: total number of tasks
                - page: current page
                - per_page: tasks per page
                - total_pages: total number of pages
        """
        if self.mode == "django-celery-results":
            return self._get_task_list_from_django_celery_results(
                search_query, page, per_page
            )
        elif self.mode == "inspect":
            return self._get_task_list_from_inspect(search_query, page, per_page)
        elif self.mode == "monitor":
            return self._get_task_list_from_worker_events(search_query, page, per_page)
        else:
            return {
                "tasks": [],
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
            }

    def _get_task_list_from_inspect(self, search_query=None, page=1, per_page=50):
        """Get tasks from worker inspection (future implementation)."""
        # TODO: Implement inspect-based task retrieval
        return {
            "tasks": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "error": "Inspect mode not yet implemented",
        }

    def _get_task_list_from_django_celery_results(
        self, search_query=None, page=1, per_page=50
    ):
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

            return {
                "tasks": tasks,
                "total_count": paginator.count,
                "page": page_obj.number,
                "per_page": per_page,
                "total_pages": paginator.num_pages,
                "has_previous": page_obj.has_previous(),
                "has_next": page_obj.has_next(),
                "previous_page": (
                    page_obj.previous_page_number() if page_obj.has_previous() else None
                ),
                "next_page": (
                    page_obj.next_page_number() if page_obj.has_next() else None
                ),
            }

        except ImportError:
            return {
                "tasks": [],
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
                "error": "django-celery-results not installed",
            }
        except Exception as e:
            return {
                "tasks": [],
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
                "error": str(e),
            }

    def _get_task_list_from_worker_events(self, search_query=None, page=1, per_page=50):
        """Get tasks from event monitor (future implementation)."""
        # TODO: Implement monitor-based task retrieval
        return {
            "tasks": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "error": "Monitor mode not yet implemented",
        }


