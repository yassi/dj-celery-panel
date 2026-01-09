from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin, messages
from celery import current_app

from .celery_utils import CeleryInspector


@staff_member_required
def index(request):
    """
    Display Celery panel dashboard.
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
            "title": "Django Celery Panel",
            "celery_status": celery_status,
        }
    )
    return render(request, "admin/dj_celery_panel/index.html", context)
