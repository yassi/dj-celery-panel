from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin


@staff_member_required
def index(request):
    """
    Display Celery panel dashboard.
    """
    context = admin.site.each_context(request)
    context.update(
        {
            "title": "Django Celery Panel",
        }
    )
    return render(request, "admin/dj_celery_panel/index.html", context)
