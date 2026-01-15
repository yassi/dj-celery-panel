from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.task_launcher, name="task_launcher"),
    path("launch/", views.launch_task, name="launch_task"),
]
