import json
from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector


@dataclass(frozen=True)
class QueueListPage:
    """Return type for queue list queries."""

    queues: list[dict]
    error: Optional[str] = None


@dataclass(frozen=True)
class QueueDetailPage:
    """Return type for single queue detail queries."""

    queue: Optional[dict]
    error: Optional[str] = None


class CeleryQueuesInterface(CeleryAbstractInterface):
    """
    Interface for retrieving queue information (both lists and individual queues).
    """

    BACKEND_KEY = "queues_backend"
    DEFAULT_BACKEND = "dj_celery_panel.celery_utils.CeleryQueuesInspectBackend"

    def get_queues(self) -> QueueListPage:
        """Get a list of all active queues."""
        return self.backend.get_queues()

    def get_queue_detail(self, queue_name: str) -> QueueDetailPage:
        """Get detailed information about a single queue."""
        return self.backend.get_queue_detail(queue_name)


class CeleryQueuesInspectBackend:
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

    def get_queue_detail(self, queue_name: str) -> QueueDetailPage:
        """Get detailed information about a single queue."""
        try:
            # Get all queues from all workers
            inspect_obj = self.app.control.inspect()
            active_queues_result = inspect_obj.active_queues()

            if not active_queues_result:
                return QueueDetailPage(
                    queue=None,
                    error=f"No workers are currently running",
                )

            # Find all workers that have this queue
            queue_detail = {
                "name": queue_name,
                "exchange": None,
                "exchange_type": None,
                "routing_key": None,
                "durable": None,
                "auto_delete": None,
                "exclusive": None,
                "arguments": None,
                "workers": [],
                "worker_details": [],
            }

            found = False

            for worker_name, worker_queues in active_queues_result.items():
                for queue in worker_queues:
                    if queue.get("name") == queue_name:
                        found = True

                        # Set queue properties (using first occurrence)
                        if queue_detail["exchange"] is None:
                            exchange = queue.get("exchange", {})
                            queue_detail["exchange"] = exchange.get("name", "N/A")
                            queue_detail["exchange_type"] = exchange.get("type", "N/A")
                            queue_detail["routing_key"] = queue.get(
                                "routing_key", "N/A"
                            )
                            queue_detail["durable"] = exchange.get("durable", False)
                            queue_detail["auto_delete"] = exchange.get(
                                "auto_delete", False
                            )
                            queue_detail["exclusive"] = queue.get("exclusive", False)
                            queue_detail["arguments"] = exchange.get("arguments", {})

                        # Add worker to the list
                        queue_detail["workers"].append(worker_name)

                        # Add detailed worker information
                        worker_info = {
                            "name": worker_name,
                            "queue_config": queue,
                        }
                        queue_detail["worker_details"].append(worker_info)

            if not found:
                return QueueDetailPage(
                    queue=None,
                    error=f"Queue '{queue_name}' not found in any active workers",
                )

            # Format complex data as JSON
            queue_detail["exchange_json"] = json.dumps(
                {
                    "name": queue_detail["exchange"],
                    "type": queue_detail["exchange_type"],
                    "durable": queue_detail["durable"],
                    "auto_delete": queue_detail["auto_delete"],
                    "arguments": queue_detail["arguments"],
                },
                indent=2,
                default=str,
            )

            queue_detail["worker_configs_json"] = json.dumps(
                [wd["queue_config"] for wd in queue_detail["worker_details"]],
                indent=2,
                default=str,
            )

            return QueueDetailPage(queue=queue_detail)

        except Exception as e:
            return QueueDetailPage(
                queue=None, error=f"Error retrieving queue details: {str(e)}"
            )
