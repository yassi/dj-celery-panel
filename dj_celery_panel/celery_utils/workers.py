import json
from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector


@dataclass(frozen=True)
class WorkerListPage:
    """Return type for worker list queries."""

    workers: list[str]
    workers_detail: list[dict]
    active_workers_count: int
    celery_available: bool
    error: Optional[str] = None


@dataclass(frozen=True)
class WorkerDetailPage:
    """Return type for single worker detail queries."""

    worker: Optional[dict]
    error: Optional[str] = None


class CeleryWorkersInterface(CeleryAbstractInterface):
    """
    Interface for retrieving worker information (both lists and individual workers).
    """

    BACKEND_KEY = "workers_backend"
    DEFAULT_BACKEND = "dj_celery_panel.celery_utils.CeleryWorkersInspectBackend"

    def get_workers(self) -> WorkerListPage:
        """Get a list of all active workers."""
        return self.backend.get_workers()

    def get_worker_detail(self, worker_id: str) -> WorkerDetailPage:
        """Get detailed information about a single worker."""
        return self.backend.get_worker_detail(worker_id)


class CeleryWorkersInspectBackend:
    """Backend for retrieving worker information from Celery inspect API."""
    
    BACKEND_DESCRIPTION = "Real-time worker status and statistics"
    DATA_SOURCE = "Celery Inspect API"

    def __init__(self, app):
        self.app = app
        self.inspector = CeleryInspector(app)

    def get_workers(self) -> WorkerListPage:
        """Get workers from celery inspect API via CeleryInspector."""
        # Use the inspector's get_status method which already handles
        # worker inspection using the stats() API
        status = self.inspector.get_status()

        return WorkerListPage(
            workers=status.get("workers", []),
            workers_detail=status.get("workers_detail", []),
            active_workers_count=status.get("active_workers_count", 0),
            celery_available=status.get("celery_available", False),
            error=status.get("error"),
        )

    def get_worker_detail(self, worker_id: str) -> WorkerDetailPage:
        """Get detailed information about a single worker."""
        try:
            # Use inspect API with destination parameter to query only the specific worker
            # This avoids fan-out calls to all workers
            inspect = self.app.control.inspect(destination=[worker_id])

            # Get stats for this specific worker
            worker_stats = inspect.stats()

            if worker_stats is None or worker_id not in worker_stats:
                return WorkerDetailPage(
                    worker=None,
                    error=f"Worker '{worker_id}' not found or not responding",
                )

            stats = worker_stats[worker_id]

            # Get additional information about the worker (all from the same targeted inspect)
            # Get active tasks for this worker
            active_tasks_result = inspect.active()
            active_tasks = (
                active_tasks_result.get(worker_id, []) if active_tasks_result else []
            )

            # Get reserved tasks for this worker
            reserved_tasks_result = inspect.reserved()
            reserved_tasks = (
                reserved_tasks_result.get(worker_id, [])
                if reserved_tasks_result
                else []
            )

            # Get scheduled tasks for this worker
            scheduled_tasks_result = inspect.scheduled()
            scheduled_tasks = (
                scheduled_tasks_result.get(worker_id, [])
                if scheduled_tasks_result
                else []
            )

            # Get registered tasks for this worker
            registered_tasks_result = inspect.registered()
            registered_tasks = (
                registered_tasks_result.get(worker_id, [])
                if registered_tasks_result
                else []
            )

            # Get active queues for this worker
            active_queues_result = inspect.active_queues()
            active_queues = (
                active_queues_result.get(worker_id, []) if active_queues_result else []
            )

            # Build comprehensive worker detail
            worker_detail = {
                "name": worker_id,
                "status": "online",
                # Pool information
                "pool": stats.get("pool", {}).get("implementation", "N/A"),
                "concurrency": stats.get("pool", {}).get("max-concurrency", "N/A"),
                "max_concurrency": stats.get("pool", {}).get("max-concurrency", "N/A"),
                "processes": stats.get("pool", {}).get("processes", []),
                # Process information
                "pid": stats.get("pid", "N/A"),
                "hostname": stats.get("hostname", worker_id),
                # Task counts
                "prefetch_count": stats.get("prefetch_count", "N/A"),
                "total": stats.get("total", {}),
                "active_tasks_count": len(active_tasks),
                "reserved_tasks_count": len(reserved_tasks),
                "scheduled_tasks_count": len(scheduled_tasks),
                # Task details (formatted as pretty JSON)
                "active_tasks": active_tasks,
                "active_tasks_json": json.dumps(active_tasks, indent=2, default=str) if active_tasks else None,
                "reserved_tasks": reserved_tasks,
                "reserved_tasks_json": json.dumps(reserved_tasks, indent=2, default=str) if reserved_tasks else None,
                "scheduled_tasks": scheduled_tasks,
                "scheduled_tasks_json": json.dumps(scheduled_tasks, indent=2, default=str) if scheduled_tasks else None,
                "registered_tasks": registered_tasks,
                "active_queues": active_queues,
                # System information (formatted as pretty JSON)
                "clock": stats.get("clock", "N/A"),
                "rusage": stats.get("rusage", {}),
                "rusage_json": json.dumps(stats.get("rusage", {}), indent=2, default=str) if stats.get("rusage") else None,
                # Broker information (formatted as pretty JSON)
                "broker": stats.get("broker", {}),
                "broker_json": json.dumps(stats.get("broker", {}), indent=2, default=str) if stats.get("broker") else None,
            }

            # Calculate total tasks executed (sum of all task counts)
            if isinstance(stats.get("total"), dict):
                worker_detail["total_tasks_executed"] = sum(
                    stats.get("total", {}).values()
                )
            else:
                worker_detail["total_tasks_executed"] = 0

            return WorkerDetailPage(worker=worker_detail)

        except Exception as e:
            return WorkerDetailPage(
                worker=None, error=f"Error retrieving worker details: {str(e)}"
            )
