# Configuration

Django Celery Panel currently works out of the box with minimal configuration.

## Basic Setup

The only required configuration is adding the app to your `INSTALLED_APPS` and including the URLs in your URL configuration.

See the [Installation](installation.md) guide for setup instructions.

## Celery Configuration

Django Celery Panel requires a properly configured Celery instance:

```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'  # Recommended for task history
CELERY_TASK_TRACK_STARTED = True     # Track when tasks start
CELERY_RESULT_EXTENDED = True        # Store extended task metadata
```

## URLs Configuration

```python
# urls.py
urlpatterns = [
    path('admin/dj-celery-panel/', include('dj_celery_panel.urls')),  # Custom path
    path('admin/', admin.site.urls),
]
```

## Security

Django Celery Panel uses Django's built-in admin authentication:

- Only staff users (`is_staff=True`) can access the panel
- All views require authentication via `@staff_member_required`
- No additional security configuration needed

## Advanced Configuration

### Swappable Backend Architecture

Django Celery Panel uses a **pluggable backend system** that allows you to customize how data is retrieved for each feature area. This makes the panel flexible and adaptable to different infrastructures.

```python
# settings.py
DJ_CELERY_PANEL_SETTINGS = {
    # Backend class for tasks interface
    "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksDjangoCeleryResultsBackend",
    
    # Backend class for workers interface
    "workers_backend": "dj_celery_panel.celery_utils.CeleryWorkersInspectBackend",
    
    # Backend class for queues interface
    "queues_backend": "dj_celery_panel.celery_utils.CeleryQueuesInspectBackend",
}
```

### Built-in Backend Classes

#### Tasks Backends

**`CeleryTasksDjangoCeleryResultsBackend`** (Default, Recommended)

Uses `django-celery-results` to provide comprehensive task history stored in your Django database.

**Features:**
- Full task history with pagination
- Search by task name or task ID
- Filter by task status
- Task results and exception information
- Complete task metadata (args, kwargs, timestamps)
- Works with any Celery broker

**Available Filters:**
- All - Show all tasks
- Pending - Tasks waiting to be executed
- Started - Currently executing tasks
- Success - Successfully completed tasks
- Failure - Failed tasks
- Retry - Tasks being retried
- Revoked - Cancelled tasks

**Requirements:**
- `django-celery-results` installed
- `CELERY_RESULT_BACKEND = 'django-db'` configured

**`CeleryTasksInspectBackend`**

Uses Celery's inspect API to provide real-time information about currently executing tasks.

**Features:**
- Real-time monitoring of active (currently executing) tasks
- Search by task name or task ID
- No database storage required
- Single fanout request to workers (optimized for performance)

**Requirements:**
- At least one running Celery worker
- Workers must be reachable via the broker

**Configuration Example:**
```python
DJ_CELERY_PANEL_SETTINGS = {
    "tasks_backend": "dj_celery_panel.celery_utils.CeleryTasksInspectBackend",
}
```

**Note:** This backend shows only live active tasks. For complete task history including finished tasks, use `CeleryTasksDjangoCeleryResultsBackend`.

#### Workers Backends

**`CeleryWorkersInspectBackend`** (Default, Recommended)

Uses Celery's inspect API to fetch real-time worker information directly from running workers.

**Features:**
- Real-time worker status
- Active, reserved, and scheduled tasks
- Worker statistics and resource usage
- Registered tasks per worker
- Active queues per worker

**Requirements:**
- At least one running Celery worker
- Workers must be reachable via the broker

#### Queues Backends

**`CeleryQueuesInspectBackend`** (Default, Recommended)

Uses Celery's inspect API to fetch queue information from running workers.

**Features:**
- List of active queues
- Exchange and routing information
- Queue bindings and configuration

**Requirements:**
- At least one running Celery worker
- Workers consuming from the queues

### Backend Information Display

Each page (Tasks, Workers, Queues) displays a compact info line at the top showing:

- **Backend Class Name**: The class being used
- **Data Source**: Where the backend retrieves its data

This helps you understand how each page is retrieving its data and verify that custom backends are configured correctly.

### Creating Custom Backends

You can implement custom backends by extending the `CeleryAbstractInterface` base class. This is useful when:

- You have a custom task storage system
- You want to aggregate data from multiple sources
- You need to integrate with external monitoring tools
- You have specific performance requirements

#### Example: Custom Tasks Backend

```python
# myapp/celery_backends.py
from dj_celery_panel.celery_utils import TaskListPage, TaskDetailPage

class CustomTasksBackend:
    """
    Custom backend that fetches tasks from an external API or custom database.
    """
    
    # Backend metadata displayed in the UI
    BACKEND_DESCRIPTION = "Aggregated task data with custom filtering"
    DATA_SOURCE = "External Monitoring API"
    
    # Define default filter behavior
    DEFAULT_FILTER = None  # or a specific default like "running"
    
    # Define available filters for the UI
    AVAILABLE_FILTERS = [
        {"value": None, "label": "All"},
        {"value": "running", "label": "Running"},
        {"value": "completed", "label": "Completed"},
        {"value": "failed", "label": "Failed"},
    ]
    
    def __init__(self, app):
        self.app = app
    
    def get_tasks(self, search_query=None, page=1, per_page=50, filter_type=None):
        """
        Fetch task list from your custom source.
        
        Args:
            search_query: Optional search string
            page: Page number
            per_page: Items per page
            filter_type: Filter value (or None for default)
        
        Returns:
            TaskListPage: Object containing tasks and pagination info
        """
        # Your custom implementation
        # Example: Fetch from external monitoring service
        tasks = self.fetch_from_custom_source(search_query, page, per_page, filter_type)
        
        return TaskListPage(
            tasks=tasks,
            total_count=len(tasks),
            page=page,
            per_page=per_page,
        )
    
    def get_task_detail(self, task_id):
        """
        Fetch detailed information about a specific task.
        
        Returns:
            TaskDetailPage: Object containing task details
        """
        task = self.fetch_task_detail(task_id)
        
        return TaskDetailPage(
            task=task,
            error=None if task else "Task not found"
        )
    
    def fetch_from_custom_source(self, search_query, page, per_page, filter_type):
        # Your custom implementation
        pass
```

#### Registering Custom Backend

```python
# settings.py
DJ_CELERY_PANEL_SETTINGS = {
    "tasks_backend": "myapp.celery_backends.CustomTasksBackend",
    # Keep default backends for workers and queues
    "workers_backend": "dj_celery_panel.celery_utils.CeleryWorkersInspectBackend",
    "queues_backend": "dj_celery_panel.celery_utils.CeleryQueuesInspectBackend",
}
```

### Backend Interface

All backends must implement specific methods and can optionally define attributes for filtering behavior:

#### Tasks Backend Interface

```python
class TasksBackend:
    # Optional: Backend metadata
    BACKEND_DESCRIPTION = "Description of what this backend does"
    DATA_SOURCE = "Where data comes from"
    
    # Optional: Filter configuration
    DEFAULT_FILTER = None  # What filter to use when none specified
    AVAILABLE_FILTERS = [  # List of available filters for UI
        {"value": None, "label": "All"},
        {"value": "active", "label": "Active"},
    ]
    
    def __init__(self, app):
        """Initialize with Celery app instance."""
        self.app = app
    
    def get_tasks(self, search_query=None, page=1, per_page=50, filter_type=None):
        """Return TaskListPage with tasks and pagination."""
        pass
    
    def get_task_detail(self, task_id):
        """Return TaskDetailPage with task details."""
        pass
```

**Key Attributes:**
- `DEFAULT_FILTER`: Value to use when no filter is specified in the request (optional)
- `AVAILABLE_FILTERS`: List of filter options to show in the UI (optional)
- `BACKEND_DESCRIPTION`: Human-readable description (optional)
- `DATA_SOURCE`: Where the backend retrieves data from (optional)

#### Workers Backend Interface

```python
class WorkersBackend(CeleryAbstractInterface):
    def get_workers(self):
        """Return WorkerListPage with active workers."""
        pass
    
    def get_worker_detail(self, worker_id):
        """Return WorkerDetailPage with worker details."""
        pass
```

#### Queues Backend Interface

```python
class QueuesBackend(CeleryAbstractInterface):
    def get_queues(self):
        """Return QueueListPage with queue information."""
        pass
    
    def get_queue_detail(self, queue_name):
        """Return QueueDetailPage with queue details."""
        pass
```

### Use Cases for Custom Backends

#### 1. Multiple Result Backends

If you store task results in multiple places (database + Redis cache), create a custom backend that checks both:

```python
class MultiSourceTasksBackend(CeleryAbstractInterface):
    def get_task_detail(self, task_id):
        # Try cache first
        task = self.get_from_redis(task_id)
        if not task:
            # Fallback to database
            task = self.get_from_database(task_id)
        return TaskDetailPage(task=task)
```

#### 2. External Monitoring Integration

Integrate with services like Datadog, New Relic, or custom monitoring:

```python
class DatadogTasksBackend(CeleryAbstractInterface):
    def get_tasks(self, search_query=None, page=1, per_page=50):
        # Fetch task metrics from Datadog API
        metrics = datadog_client.get_celery_metrics()
        return TaskListPage(tasks=self.format_metrics(metrics), ...)
```

#### 3. Performance Optimization

Implement caching or aggregation for high-traffic environments:

```python
class CachedWorkersBackend(CeleryWorkersInspectBackend):
    def get_workers(self):
        cache_key = "celery_workers"
        workers = cache.get(cache_key)
        if not workers:
            workers = super().get_workers()
            cache.set(cache_key, workers, timeout=30)  # 30 second cache
        return workers
```

### Benefits of Swappable Backends

1. **No Vendor Lock-in**: Switch data sources without changing the UI
2. **Incremental Migration**: Move from one system to another gradually
3. **A/B Testing**: Test different implementations side by side
4. **Custom Business Logic**: Add filtering, transformation, or aggregation
5. **Integration**: Connect with existing monitoring infrastructure
6. **Performance Tuning**: Optimize data fetching for your specific needs

### Requirements

The default backends require:
- **Running Celery workers** for worker and queue monitoring
- **django-celery-results** installed and configured for task history
- **Proper Celery broker** (Redis, RabbitMQ, etc.) configured and running

Custom backends may have different requirements based on their implementation.
