# Installation

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

## 4. Run Migrations

```bash
python manage.py migrate
```

## 5. Access the Panel

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to `http://127.0.0.1:8000/admin/`

3. Look for the "DJ_CELERY_PANEL" section

4. Click to access the Celery Panel

That's it!
