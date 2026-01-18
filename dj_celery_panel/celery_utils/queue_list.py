from .inspector import CeleryInspector


class CeleryQueueListInterface:
    """
    Interface for retrieving queue information from various sources.
    Supports multiple modes: inspect, config, etc.
    """

    def __init__(self, app, mode="inspect"):
        """
        Initialize the queue list interface.

        Args:
            app: Celery application instance
            mode: str - 'inspect' or 'config'
        """
        self.app = app
        self.mode = mode
        self.inspector = CeleryInspector(app)

    def get_queues(self):
        """
        Get queue information based on the configured mode.

        Returns:
            dict with:
                - queues: list of queue dictionaries
                - error: optional error message
        """
        if self.mode == "inspect":
            return self._get_queues_from_inspect()
        elif self.mode == "config":
            return self._get_queues_from_config()
        else:
            return {"queues": [], "error": "Invalid mode"}

    def _get_queues_from_inspect(self):
        """Get active queues from worker inspection via CeleryInspector."""
        # Use the inspector's get_queues method which already handles
        # queue inspection using the active_queues() API
        return self.inspector.get_queues()

    def _get_queues_from_config(self):
        """Get queues from celery configuration (future implementation)."""
        # TODO: Implement config-based queue retrieval
        # This would read from CELERY_QUEUES configuration
        return {
            "queues": [],
            "error": "Config mode not yet implemented",
        }
