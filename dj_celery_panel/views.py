from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin, messages
from celery import current_app

from django.conf import settings

from .celery_utils import CeleryInspector, CeleryTaskListInterface


@staff_member_required
def index(request):
    """
    Display Celery panel overview with static configuration information.
    Fast-loading page with no inspect API calls.
    """
    inspector = CeleryInspector(current_app)

    # Get static configuration info (no broker calls)
    config = inspector.get_configuration_info()

    # Get registered tasks (local operation)
    registered_tasks = inspector.get_registered_tasks(exclude_internal=True)

    # Get periodic tasks from beat schedule
    periodic_tasks = inspector.get_periodic_tasks()

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Overview",
            "current_tab": "overview",
            "config": config,
            "registered_tasks": registered_tasks,
            "registered_tasks_count": len(registered_tasks),
            "periodic_tasks": periodic_tasks,
            "periodic_tasks_count": len(periodic_tasks),
        }
    )
    return render(request, "admin/dj_celery_panel/index.html", context)


@staff_member_required
def workers(request):
    """
    Display active Celery workers with real-time inspection data.
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
    return render(request, "admin/dj_celery_panel/workers.html", context)


@staff_member_required
def tasks(request):
    """
    Display task execution history with pagination and search.
    """
    # Get configuration
    panel_settings = getattr(settings, "DJ_CELERY_PANEL_SETTINGS", {})
    task_result_mode = panel_settings.get("task_result_mode", "django-celery-results")

    # Get pagination and search parameters
    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    search_query = request.GET.get("search", "").strip()
    per_page = 50

    # Get tasks using the interface
    task_interface = CeleryTaskListInterface(current_app, mode=task_result_mode)
    task_data = task_interface.get_tasks(
        search_query=search_query if search_query else None,
        page=page,
        per_page=per_page,
    )

    # Handle errors
    if task_data.get("error"):
        messages.warning(request, f"Task retrieval warning: {task_data['error']}")

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Tasks",
            "current_tab": "tasks",
            "tasks": task_data.get("tasks", []),
            "total_count": task_data.get("total_count", 0),
            "page": task_data.get("page", 1),
            "per_page": task_data.get("per_page", per_page),
            "total_pages": task_data.get("total_pages", 0),
            "has_previous": task_data.get("has_previous", False),
            "has_next": task_data.get("has_next", False),
            "previous_page": task_data.get("previous_page"),
            "next_page": task_data.get("next_page"),
            "search_query": search_query,
            "task_result_mode": task_result_mode,
        }
    )
    return render(request, "admin/dj_celery_panel/tasks.html", context)


@staff_member_required
def queues(request):
    """
    Display Celery queues information from active workers.
    """
    inspector = CeleryInspector(current_app)
    queue_result = inspector.get_queues()

    if queue_result.get("error"):
        messages.warning(
            request, f"Could not retrieve queue information: {queue_result['error']}"
        )

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Queues",
            "current_tab": "queues",
            "queues": queue_result.get("queues", []),
        }
    )
    return render(request, "admin/dj_celery_panel/queues.html", context)


@staff_member_required
def configuration(request):
    """
    Display Celery configuration.
    """
    inspector = CeleryInspector(current_app)
    config = inspector.get_configuration_info()

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Configuration",
            "config": config,
            "current_tab": "configuration",
        }
    )
    return render(request, "admin/dj_celery_panel/configuration.html", context)
