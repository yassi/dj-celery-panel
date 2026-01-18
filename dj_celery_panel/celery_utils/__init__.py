"""
Celery utilities module.

This module provides interface classes for interacting with Celery
in different ways (inspect API, result backends, event monitors, etc.).
"""

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector
from .queue_list import (
    CeleryQueueListInterface,
    CeleryQueueListInspectBackend,
    QueueListPage,
)
from .tasks import (
    CeleryTasksDjangoCeleryResultsBackend,
    CeleryTasksInterface,
    TaskDetailPage,
    TaskListPage,
)
from .worker_list import (
    CeleryWorkerListInterface,
    CeleryWorkerListInspectBackend,
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
    # Worker List
    "CeleryWorkerListInterface",
    "CeleryWorkerListInspectBackend",
    "WorkerListPage",
    # Queue List
    "CeleryQueueListInterface",
    "CeleryQueueListInspectBackend",
    "QueueListPage",
]
