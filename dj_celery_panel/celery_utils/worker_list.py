from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector


@dataclass(frozen=True)
class WorkerListPage:
    workers: list[str]
    workers_detail: list[dict]
    active_workers_count: int
    celery_available: bool
    error: Optional[str] = None


class CeleryWorkerListInterface(CeleryAbstractInterface):
    """
    Interface for retrieving worker information from various sources.
    """

    BACKEND_KEY = "worker_backend"
    DEFAULT_BACKEND = "dj_celery_panel.celery_utils.CeleryWorkerListInspectBackend"

    def get_workers(self) -> WorkerListPage:
        return self.backend.get_workers()


class CeleryWorkerListInspectBackend:
    """Backend for retrieving worker information from Celery inspect API."""

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
