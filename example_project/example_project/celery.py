import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

app = Celery("example_project")

# Load task modules from all registered Django app configs.
# The 'namespace' parameter tells Celery to look for all settings
# with a 'CELERY_' prefix in Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
