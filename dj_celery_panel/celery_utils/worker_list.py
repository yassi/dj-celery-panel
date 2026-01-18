from .inspector import CeleryInspector


class CeleryWorkerListInterface:
    """
    Interface for retrieving worker information from various sources.
    Supports multiple modes: inspect, monitor, etc.
    """

    def __init__(self, app, mode="inspect"):
        """
        Initialize the worker list interface.

        Args:
            app: Celery application instance
            mode: str - 'inspect' or 'monitor'
        """
        self.app = app
        self.mode = mode
        self.inspector = CeleryInspector(app)

    def get_workers(self):
        """
        Get worker information based on the configured mode.

        Returns:
            dict with:
                - workers: list of worker dictionaries with detailed info
                - workers_detail: list of worker detail dictionaries
                - active_workers_count: int
                - celery_available: bool
                - error: optional error message
        """
        if self.mode == "inspect":
            return self._get_workers_from_inspect()
        elif self.mode == "monitor":
            return self._get_workers_from_monitor()
        else:
            return {
                "workers": [],
                "workers_detail": [],
                "active_workers_count": 0,
                "celery_available": False,
                "error": "Invalid mode",
            }

    def _get_workers_from_inspect(self):
        """Get workers from celery inspect API via CeleryInspector."""
        # Use the inspector's get_status method which already handles
        # worker inspection using the stats() API
        status = self.inspector.get_status()

        return {
            "workers": status.get("workers", []),
            "workers_detail": status.get("workers_detail", []),
            "active_workers_count": status.get("active_workers_count", 0),
            "celery_available": status.get("celery_available", False),
            "error": status.get("error"),
        }

    def _get_workers_from_monitor(self):
        """Get workers from event monitor (future implementation)."""
        # TODO: Implement monitor-based worker retrieval
        return {
            "workers": [],
            "workers_detail": [],
            "active_workers_count": 0,
            "celery_available": False,
            "error": "Monitor mode not yet implemented",
        }
