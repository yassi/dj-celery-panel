# Installation

## Prerequisites

- Django 4.2+
- Celery 5.0+
- A running Celery broker (Redis, RabbitMQ, etc.)
- At least one Celery worker (for monitoring functionality)

## 1. Install the Package

```bash
pip install dj-celery-panel
```

## 2. Add to Django Settings

Add `dj_celery_panel` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dj_celery_panel',  # Add this
    # ... your other apps
]
```

## 3. Include URLs

Add the Celery Panel URLs to your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/dj-celery-panel/', include('dj_celery_panel.urls')),
    path('admin/', admin.site.urls),
]
```

## 4. Configure Celery

Ensure you have Celery properly configured in your Django settings:

```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Your broker URL
CELERY_RESULT_BACKEND = 'django-db'  # or your preferred backend
```

## 5. Run Migrations

```bash
python manage.py migrate
```

## 6. Start Celery Worker

The panel requires at least one running Celery worker to display worker and queue information:

```bash
celery -A your_project worker --loglevel=info
```

## 7. Access the Panel

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to `http://127.0.0.1:8000/admin/`

3. Look for the "DJ_CELERY_PANEL" section

4. Click to access workers, tasks, queues, and periodic tasks

That's it!
