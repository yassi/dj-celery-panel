"""
Example Celery tasks for testing dj-celery-panel.

These tasks are designed to test different aspects of the Celery panel:
- Quick tasks that complete immediately
- Long-running tasks that stay active
- Tasks that schedule other tasks with eta/countdown
"""

import time
from celery import shared_task
from datetime import timedelta


@shared_task
def quick_noop_task(message="Hello from quick task"):
    """
    A simple task that completes immediately.

    Useful for testing:
    - Task completion
    - Task results
    - Worker throughput

    Args:
        message: A message to return

    Returns:
        str: The message passed in
    """
    return f"Quick task completed: {message}"


@shared_task
def slow_task(duration=10, task_name="slow_task"):
    """
    A task that sleeps for a specified duration.

    Useful for testing:
    - Active tasks display
    - Task monitoring while running
    - Worker state during task execution

    Args:
        duration: Number of seconds to sleep (default: 10)
        task_name: Name to identify this task instance

    Returns:
        str: Completion message with duration
    """
    print(f"[{task_name}] Starting slow task, will sleep for {duration} seconds...")
    time.sleep(duration)
    print(f"[{task_name}] Slow task completed after {duration} seconds")
    return f"Slow task '{task_name}' completed after {duration} seconds"


@shared_task
def spawn_scheduled_tasks(count=5, delay_seconds=5, use_eta=True, quick_task=True):
    """
    Spawns multiple tasks scheduled to run in the future.

    Useful for testing:
    - Scheduled tasks display
    - Tasks with eta vs countdown
    - Reserved tasks queue
    - Bulk task scheduling

    Args:
        count: Number of tasks to spawn (default: 5)
        delay_seconds: Seconds to delay each task (default: 5)
        use_eta: If True, use eta; if False, use countdown (default: True)
        quick_task: If True, spawn quick tasks; if False, spawn slow tasks (default: True)

    Returns:
        dict: Information about spawned tasks
    """
    spawned_task_ids = []
    task_type = "quick_noop_task" if quick_task else "slow_task"

    for i in range(count):
        delay = delay_seconds * (i + 1)

        if quick_task:
            if use_eta:
                # Schedule with eta (absolute time)
                result = quick_noop_task.apply_async(
                    args=[f"Scheduled task #{i + 1}"], eta=timedelta(seconds=delay)
                )
            else:
                # Schedule with countdown (relative time)
                result = quick_noop_task.apply_async(
                    args=[f"Scheduled task #{i + 1}"], countdown=delay
                )
        else:
            if use_eta:
                result = slow_task.apply_async(
                    args=[3, f"scheduled_slow_{i + 1}"], eta=timedelta(seconds=delay)
                )
            else:
                result = slow_task.apply_async(
                    args=[3, f"scheduled_slow_{i + 1}"], countdown=delay
                )

        spawned_task_ids.append(result.id)
        print(
            f"Scheduled {task_type} #{i + 1} with delay of {delay}s (task_id: {result.id})"
        )

    return {
        "spawned_count": count,
        "task_ids": spawned_task_ids,
        "task_type": task_type,
        "scheduling_method": "eta" if use_eta else "countdown",
        "delay_seconds": delay_seconds,
    }


@shared_task
def spawn_bulk_immediate_tasks(count=10):
    """
    Spawns multiple tasks to execute immediately.

    Useful for testing:
    - Worker load
    - Active tasks count
    - Task throughput
    - Queue pressure

    Args:
        count: Number of tasks to spawn (default: 10)

    Returns:
        dict: Information about spawned tasks
    """
    spawned_task_ids = []

    for i in range(count):
        result = quick_noop_task.apply_async(args=[f"Bulk task #{i + 1}"])
        spawned_task_ids.append(result.id)

    return {
        "spawned_count": count,
        "task_ids": spawned_task_ids,
    }


@shared_task
def failing_task(error_message="Intentional test error"):
    """
    A task that always fails with an exception.

    Useful for testing:
    - Error handling
    - Failed task display
    - Task retry behavior

    Args:
        error_message: The error message to raise

    Raises:
        Exception: Always raises an exception
    """
    print(f"Failing task is about to raise an error: {error_message}")
    raise Exception(error_message)


@shared_task(bind=True, max_retries=3)
def retrying_task(self, fail_times=2):
    """
    A task that fails a specified number of times before succeeding.

    Useful for testing:
    - Task retry mechanism
    - Retry count display
    - Task state transitions

    Args:
        fail_times: Number of times to fail before succeeding (default: 2)

    Returns:
        str: Success message with retry count
    """
    attempt = self.request.retries
    print(f"Retrying task attempt #{attempt + 1}")

    if attempt < fail_times:
        print(f"Failing attempt #{attempt + 1}, will retry...")
        raise self.retry(countdown=3)

    return f"Retrying task succeeded after {attempt} retries"


# ===== PERIODIC TASKS =====

@shared_task
def health_check():
    """
    Periodic health check task that runs every 5 minutes.
    
    Useful for testing:
    - Periodic task execution
    - System monitoring
    - Regular task scheduling
    
    Returns:
        dict: Health check status
    """
    from datetime import datetime
    print(f"[Health Check] Running at {datetime.now()}")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "System is running normally"
    }


@shared_task
def cleanup_old_results():
    """
    Periodic task to clean up old task results (runs daily).
    
    Deletes task results older than 7 days to prevent database bloat.
    
    Returns:
        dict: Cleanup statistics
    """
    from django_celery_results.models import TaskResult
    from datetime import timedelta
    from django.utils import timezone
    
    cutoff_date = timezone.now() - timedelta(days=7)
    count_before = TaskResult.objects.count()
    deleted = TaskResult.objects.filter(date_created__lt=cutoff_date).delete()
    count_after = TaskResult.objects.count()
    
    result = {
        "deleted_count": deleted[0] if deleted else 0,
        "total_before": count_before,
        "total_after": count_after,
        "cutoff_date": cutoff_date.isoformat(),
    }
    
    print(f"[Cleanup] Deleted {result['deleted_count']} old task results")
    return result


@shared_task
def generate_hourly_report():
    """
    Periodic task to generate a report every hour.
    
    Useful for testing:
    - Hourly scheduled tasks
    - Report generation workflows
    - Time-based automation
    
    Returns:
        dict: Report information
    """
    from datetime import datetime
    print(f"[Report] Generating hourly report at {datetime.now()}")
    
    # Simulate report generation
    return {
        "report_type": "hourly",
        "generated_at": datetime.now().isoformat(),
        "status": "completed",
        "data_points": 42,
    }


@shared_task
def send_periodic_notification():
    """
    Periodic task that runs every 30 seconds (for testing).
    
    Useful for testing:
    - Frequent periodic tasks
    - Quick feedback on schedule changes
    - Beat scheduler health
    
    Returns:
        str: Notification message
    """
    from datetime import datetime
    message = f"Periodic notification sent at {datetime.now().strftime('%H:%M:%S')}"
    print(f"[Notification] {message}")
    return message
