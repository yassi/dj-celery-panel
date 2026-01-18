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

You can customize the backend classes used by Django Celery Panel:

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

### Available Backend Classes

#### Tasks Backends
- `CeleryTasksDjangoCeleryResultsBackend` - Uses django-celery-results for task history (recommended)

#### Workers Backends
- `CeleryWorkersInspectBackend` - Uses Celery's inspect API for real-time worker information

#### Queues Backends
- `CeleryQueuesInspectBackend` - Uses Celery's inspect API for queue information

### Requirements

The panel requires:
- **Running Celery workers** for worker and queue monitoring
- **django-celery-results** installed and configured for task history
- **Proper Celery broker** (Redis, RabbitMQ, etc.) configured and running
