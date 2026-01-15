from django.urls import path
from . import views

app_name = "dj_celery_panel"

urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/", views.tasks, name="tasks"),
    path("periodic-tasks/", views.periodic_tasks, name="periodic_tasks"),
    path("queues/", views.queues, name="queues"),
    path("configuration/", views.configuration, name="configuration"),
]
