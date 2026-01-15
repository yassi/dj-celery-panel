from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from app.tasks import (
    quick_noop_task,
    slow_task,
    spawn_scheduled_tasks,
    spawn_bulk_immediate_tasks,
    failing_task,
    retrying_task,
)


@staff_member_required
def task_launcher(request):
    """
    Display the task launcher interface.
    """
    return render(request, "task_launcher.html")


@staff_member_required
@require_http_methods(["POST"])
def launch_task(request):
    """
    Launch a task based on the request parameters.
    """
    task_type = request.POST.get("task_type")

    try:
        if task_type == "quick":
            message = request.POST.get("message", "Manual test from launcher")
            result = quick_noop_task.delay(message)
            return JsonResponse(
                {
                    "success": True,
                    "task_id": result.id,
                    "task_type": "Quick Noop Task",
                    "message": f"Launched with message: {message}",
                }
            )

        elif task_type == "slow":
            duration = int(request.POST.get("duration", 10))
            task_name = request.POST.get("task_name", "launcher_slow")
            result = slow_task.delay(duration, task_name)
            return JsonResponse(
                {
                    "success": True,
                    "task_id": result.id,
                    "task_type": "Slow Task",
                    "message": f"Launched to run for {duration} seconds",
                }
            )

        elif task_type == "scheduled":
            count = int(request.POST.get("count", 5))
            delay = int(request.POST.get("delay", 5))
            use_eta = request.POST.get("use_eta", "true") == "true"
            quick = request.POST.get("quick", "true") == "true"
            result = spawn_scheduled_tasks.delay(count, delay, use_eta, quick)
            return JsonResponse(
                {
                    "success": True,
                    "task_id": result.id,
                    "task_type": "Spawn Scheduled Tasks",
                    "message": f"Spawning {count} tasks with {delay}s delays",
                }
            )

        elif task_type == "bulk":
            count = int(request.POST.get("count", 10))
            result = spawn_bulk_immediate_tasks.delay(count)
            return JsonResponse(
                {
                    "success": True,
                    "task_id": result.id,
                    "task_type": "Spawn Bulk Tasks",
                    "message": f"Spawning {count} immediate tasks",
                }
            )

        elif task_type == "fail":
            error_msg = request.POST.get("error_message", "Test error from launcher")
            result = failing_task.delay(error_msg)
            return JsonResponse(
                {
                    "success": True,
                    "task_id": result.id,
                    "task_type": "Failing Task",
                    "message": f"Launched task that will fail: {error_msg}",
                }
            )

        elif task_type == "retry":
            fail_times = int(request.POST.get("fail_times", 2))
            result = retrying_task.delay(fail_times)
            return JsonResponse(
                {
                    "success": True,
                    "task_id": result.id,
                    "task_type": "Retrying Task",
                    "message": f"Launched task that will retry {fail_times} times",
                }
            )

        else:
            return JsonResponse(
                {"success": False, "error": f"Unknown task type: {task_type}"},
                status=400,
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
