import importlib


class CeleryAbstractInterface:
    """
    Abstract base class for all Celery panel interfaces.

    This class handles the common pattern of:
    1. Loading backend class path from Django settings
    2. Dynamically importing the backend class
    3. Instantiating the backend with the Celery app
    4. Providing backend metadata for display in the UI

    Subclasses must define:
    - BACKEND_KEY: The settings key to look for (e.g., "tasks_backend")
    - DEFAULT_BACKEND: The default backend class path if not configured
    
    Backend classes should define:
    - BACKEND_DESCRIPTION: Short description of backend capabilities
    - DATA_SOURCE: Where the backend retrieves its data from
    """

    BACKEND_KEY = None
    DEFAULT_BACKEND = None

    def __init__(self, app, backend_path=None):
        """
        Initialize the interface with a Celery app and optional backend override.

        Args:
            app: The Celery application instance
            backend_path: Optional backend class path string to override settings
        """
        if backend_path is None:
            backend_path = self._get_backend_path_from_settings()

        backend_class = self._load_backend_class(backend_path)
        self.backend = backend_class(app)

    def _get_backend_path_from_settings(self):
        """Load backend class path from Django settings or use default."""
        from django.conf import settings

        if self.BACKEND_KEY is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define BACKEND_KEY"
            )

        panel_settings = getattr(settings, "DJ_CELERY_PANEL_SETTINGS", {})
        return panel_settings.get(self.BACKEND_KEY, self.DEFAULT_BACKEND)

    def _load_backend_class(self, backend_path):
        """
        Dynamically load and return a backend class from its module path.

        Args:
            backend_path: Full dotted path to the backend class

        Returns:
            The backend class (not an instance)
        """
        module_path, class_name = backend_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def get_backend_info(self):
        """
        Get information about the currently configured backend.
        
        Returns:
            dict: Backend metadata including name, module, full path, description, and data source
        """
        return {
            "name": self.backend.__class__.__name__,
            "module": self.backend.__class__.__module__,
            "full_path": f"{self.backend.__class__.__module__}.{self.backend.__class__.__name__}",
            "description": getattr(self.backend.__class__, "BACKEND_DESCRIPTION", "No description available"),
            "data_source": getattr(self.backend.__class__, "DATA_SOURCE", "Unknown"),
        }
