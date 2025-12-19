from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin


@staff_member_required
def index(request):
    """
    Display all configured cache instances with their panel abilities.
    """
    # Build cache info with panel abilities
    context = admin.site.each_context(request)
    context.update(
        {
            "title": "DJ Cache Panel - Instances",
        }
    )
    return render(request, "admin/dj_celery_panel/index.html", context)
