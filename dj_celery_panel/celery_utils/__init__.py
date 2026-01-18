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
from .task_detail import (
    CeleryTaskInstanceDetailInterface,
    CeleryTaskDetailDjangoCeleryResultsBackend,
    TaskDetailPage,
)
from .task_list import (
    CeleryTaskListInterface,
    CeleryTaskListDjangoCeleryResultsBackend,
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
    # Task List
    "CeleryTaskListInterface",
    "CeleryTaskListDjangoCeleryResultsBackend",
    "TaskListPage",
    # Task Detail
    "CeleryTaskInstanceDetailInterface",
    "CeleryTaskDetailDjangoCeleryResultsBackend",
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
