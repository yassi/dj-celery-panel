from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector


@dataclass(frozen=True)
class QueueListPage:
    queues: list[dict]
    error: Optional[str] = None


class CeleryQueueListInterface(CeleryAbstractInterface):
    """
    Interface for retrieving queue information from various sources.
    """

    BACKEND_KEY = "queue_backend"
    DEFAULT_BACKEND = "dj_celery_panel.celery_utils.CeleryQueueListInspectBackend"

    def get_queues(self) -> QueueListPage:
        return self.backend.get_queues()


class CeleryQueueListInspectBackend:
    """Backend for retrieving queue information from Celery inspect API."""

    def __init__(self, app):
        self.app = app
        self.inspector = CeleryInspector(app)

    def get_queues(self) -> QueueListPage:
        """Get active queues from worker inspection via CeleryInspector."""
        # Use the inspector's get_queues method which already handles
        # queue inspection using the active_queues() API
        result = self.inspector.get_queues()
        return QueueListPage(queues=result.get("queues", []), error=result.get("error"))
