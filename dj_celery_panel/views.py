from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin, messages
from celery import current_app

from .celery_utils import (
    CeleryInspector,
    CeleryQueueListInterface,
    CeleryTasksInterface,
    CeleryWorkerListInterface,
)


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
    # Get workers using the interface
    worker_interface = CeleryWorkerListInterface(current_app)
    worker_result = worker_interface.get_workers()

    # Use Django's messaging framework for errors and notifications
    if worker_result.error:
        messages.error(request, worker_result.error)
    elif worker_result.celery_available and worker_result.active_workers_count > 0:
        messages.success(
            request,
            f"Celery is running with {worker_result.active_workers_count} active worker(s).",
        )

    # Get configuration for sidebar
    inspector = CeleryInspector(current_app)
    config = inspector.get_configuration_info()

    # Format result to match existing template expectations
    celery_status = {
        "celery_available": worker_result.celery_available,
        "workers": worker_result.workers,
        "workers_detail": worker_result.workers_detail,
        "active_workers_count": worker_result.active_workers_count,
        "error": worker_result.error,
        "config": config,
    }

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
    # Get pagination and search parameters
    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    search_query = request.GET.get("search", "").strip()
    per_page = 50

    # Get tasks using the interface
    task_interface = CeleryTasksInterface(current_app)
    task_data = task_interface.get_tasks(
        search_query=search_query if search_query else None,
        page=page,
        per_page=per_page,
    )

    # Handle errors
    if task_data.error:
        messages.warning(request, f"Task retrieval warning: {task_data.error}")

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Tasks",
            "current_tab": "tasks",
            "tasks": task_data.tasks,
            "total_count": task_data.total_count,
            "page": task_data.page,
            "per_page": task_data.per_page,
            "total_pages": task_data.total_pages,
            "has_previous": task_data.has_previous,
            "has_next": task_data.has_next,
            "previous_page": task_data.previous_page,
            "next_page": task_data.next_page,
            "search_query": search_query,
        }
    )
    return render(request, "admin/dj_celery_panel/tasks.html", context)


@staff_member_required
def queues(request):
    """
    Display Celery queues information from active workers.
    """
    # Get queues using the interface
    queue_interface = CeleryQueueListInterface(current_app)
    queue_result = queue_interface.get_queues()

    if queue_result.error:
        messages.warning(
            request, f"Could not retrieve queue information: {queue_result.error}"
        )

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Queues",
            "current_tab": "queues",
            "queues": queue_result.queues,
        }
    )
    return render(request, "admin/dj_celery_panel/queues.html", context)


@staff_member_required
def task_detail(request, task_id):
    """
    Display detailed information about a specific task instance.
    """
    # Get task details using the interface
    task_interface = CeleryTasksInterface(current_app)
    result = task_interface.get_task_detail(task_id)

    # Handle errors
    if result.error:
        messages.error(request, f"Error retrieving task: {result.error}")

    context = admin.site.each_context(request)
    context.update(
        {
            "title": f"Django Celery Panel - Task {task_id[:8]}...",
            "current_tab": "tasks",
            "task": result.task,
        }
    )
    return render(request, "admin/dj_celery_panel/task_detail.html", context)


@staff_member_required
def configuration(request):
    """
    Display Celery configuration and DJ Celery Panel settings.
    """
    from django.conf import settings

    inspector = CeleryInspector(current_app)
    config = inspector.get_configuration_info()

    # Get DJ Celery Panel settings
    panel_settings = getattr(settings, "DJ_CELERY_PANEL_SETTINGS", {})

    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel - Configuration",
            "config": config,
            "panel_settings": panel_settings,
            "current_tab": "configuration",
        }
    )
    return render(request, "admin/dj_celery_panel/configuration.html", context)
