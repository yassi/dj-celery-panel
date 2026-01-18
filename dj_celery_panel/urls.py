from django.urls import path
from . import views

app_name = "dj_celery_panel"

urlpatterns = [
    path("", views.index, name="index"),
    path("workers/", views.workers, name="workers"),
    path("workers/<str:worker_id>/", views.worker_detail, name="worker_detail"),
    path("tasks/", views.tasks, name="tasks"),
    path("tasks/<str:task_id>/", views.task_detail, name="task_detail"),
    path("queues/", views.queues, name="queues"),
    path("configuration/", views.configuration, name="configuration"),
]
