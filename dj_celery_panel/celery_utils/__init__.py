"""
Celery utilities module.

This module provides interface classes for interacting with Celery
in different ways (inspect API, result backends, event monitors, etc.).
"""

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector
from .queues import (
    CeleryQueuesInspectBackend,
    CeleryQueuesInterface,
    QueueDetailPage,
    QueueListPage,
)
from .tasks import (
    CeleryTasksDjangoCeleryResultsBackend,
    CeleryTasksInterface,
    TaskDetailPage,
    TaskListPage,
)
from .workers import (
    CeleryWorkersInspectBackend,
    CeleryWorkersInterface,
    WorkerDetailPage,
    WorkerListPage,
)

__all__ = [
    # Base classes
    "CeleryAbstractInterface",
    # Inspector
    "CeleryInspector",
    # Tasks
    "CeleryTasksInterface",
    "CeleryTasksDjangoCeleryResultsBackend",
    "TaskListPage",
    "TaskDetailPage",
    # Workers
    "CeleryWorkersInterface",
    "CeleryWorkersInspectBackend",
    "WorkerListPage",
    "WorkerDetailPage",
    # Queues
    "CeleryQueuesInterface",
    "CeleryQueuesInspectBackend",
    "QueueListPage",
    "QueueDetailPage",
]
