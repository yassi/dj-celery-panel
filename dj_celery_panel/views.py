from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin, messages
from celery import current_app

from .celery_utils import CeleryInspector


@staff_member_required
def index(request):
    """
    Display Celery panel dashboard - Active Workers view.
    """
    # Get celery status using inspector
    inspector = CeleryInspector(current_app)
    celery_status = inspector.get_status()

    # Use Django's messaging framework for errors and notifications
    if celery_status.get("error"):
        messages.error(request, celery_status["error"])
    elif (
        celery_status.get("celery_available")
        and celery_status.get("active_workers_count", 0) > 0
    ):
        messages.success(
            request,
            f"Celery is running with {celery_status['active_workers_count']} active worker(s).",
        )

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Active Workers",
            "celery_status": celery_status,
            "current_tab": "workers",
        }
    )
    return render(request, "admin/dj_celery_panel/index.html", context)


@staff_member_required
def tasks(request):
    """
    Display registered Celery tasks.
    """
    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Tasks",
            "current_tab": "tasks",
        }
    )
    return render(request, "admin/dj_celery_panel/tasks.html", context)


@staff_member_required
def periodic_tasks(request):
    """
    Display periodic tasks and beat schedule.
    """
    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Periodic Tasks",
            "current_tab": "periodic_tasks",
        }
    )
    return render(request, "admin/dj_celery_panel/periodic_tasks.html", context)


@staff_member_required
def queues(request):
    """
    Display Celery queues information.
    """
    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Queues",
            "current_tab": "queues",
        }
    )
    return render(request, "admin/dj_celery_panel/queues.html", context)


@staff_member_required
def configuration(request):
    """
    Display Celery configuration.
    """
    inspector = CeleryInspector(current_app)
    celery_status = inspector.get_status()

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Configuration",
            "celery_status": celery_status,
            "current_tab": "configuration",
        }
    )
    return render(request, "admin/dj_celery_panel/configuration.html", context)
