class CeleryTaskInstanceDetailInterface:
    """
    Utility class that powers the task detail view.

    Similar to the task list interface, there are many ways to generate a task detail
    view and this class provides a unified interface for all these approaches.
    """

    def __init__(self, app, mode="django-celery-results"):
        self.app = app
        self.mode = mode

    def get_task_detail(self, task_id):
        """
        Get detailed information about a specific task instance.

        Args:
            task_id: str - The UUID of the task

        Returns:
            dict with task details or error information
        """
        if self.mode == "django-celery-results":
            return self._get_task_detail_from_db(task_id)
        elif self.mode == "inspect":
            return self._get_task_detail_from_inspect(task_id)
        elif self.mode == "monitor":
            return self._get_task_detail_from_monitor(task_id)
        else:
            return {"task": None, "error": "Invalid mode"}

    def _get_task_detail_from_db(self, task_id):
        """Get task details from django-celery-results database."""
        try:
            from django_celery_results.models import TaskResult

            task = TaskResult.objects.filter(task_id=task_id).first()

            if not task:
                return {"task": None, "error": "Task not found"}

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

            return {"task": task_detail, "error": None}

        except ImportError:
            return {
                "task": None,
                "error": "django-celery-results not installed",
            }
        except Exception as e:
            return {"task": None, "error": str(e)}

    def _get_task_detail_from_inspect(self, task_id):
        """Get task details from worker inspection (future implementation)."""
        # TODO: Implement inspect-based task detail retrieval
        return {
            "task": None,
            "error": "Inspect mode not yet implemented",
        }

    def _get_task_detail_from_monitor(self, task_id):
        """Get task details from event monitor (future implementation)."""
        # TODO: Implement monitor-based task detail retrieval
        return {
            "task": None,
            "error": "Monitor mode not yet implemented",
        }
