class CeleryInspector:
    """
    High level interface celery and celery information. This class will generally
    wrap around the celery api (particularly celery.Celery.control) to provide
    presentation level data for use in dashboards and admin interfaces.
    """

    def __init__(self, app):
        self.app = app

    def get_configuration_info(self):
        """
        Get Celery configuration information for display.
        Returns a dictionary with broker type, result backend, and other config details.
        """
        config_info = {
            "broker_url": None,
            "broker_type": None,
            "result_backend": None,
            "result_backend_type": None,
            "timezone": None,
            "task_serializer": None,
            "result_serializer": None,
            "accept_content": None,
            # Task execution settings
            "task_acks_late": None,
            "task_track_started": None,
            "task_time_limit": None,
            "task_soft_time_limit": None,
            "task_ignore_result": None,
            "task_always_eager": None,
            # Queue settings
            "create_missing_queues": None,
            "default_queue": None,
            "default_exchange": None,
            "default_routing_key": None,
            # Worker settings
            "worker_prefetch_multiplier": None,
            "worker_max_tasks_per_child": None,
            # Result settings
            "result_expires": None,
        }

        try:
            # Get broker URL and determine broker type
            broker_url = self.app.conf.get("broker_url", "")
            config_info["broker_url"] = broker_url

            if broker_url:
                # Check for Redis broker (redis://, rediss://, redis+socket://)
                if broker_url.startswith(("redis://", "rediss://", "redis+socket://")):
                    config_info["broker_type"] = "Redis"
                # Check for AMQP brokers (amqp://, amqps://, pyamqp://, librabbitmq://)
                elif broker_url.startswith(
                    ("amqp://", "amqps://", "pyamqp://", "librabbitmq://")
                ):
                    config_info["broker_type"] = "RabbitMQ (AMQP)"
                # Check for Amazon SQS (sqs://, sqss://)
                elif broker_url.startswith(("sqs://", "sqss://")):
                    config_info["broker_type"] = "Amazon SQS"
                # Check for MongoDB (mongodb://)
                elif broker_url.startswith("mongodb://"):
                    config_info["broker_type"] = "MongoDB"
                # Check for Kafka (kafka://)
                elif broker_url.startswith("kafka://"):
                    config_info["broker_type"] = "Apache Kafka"
                # Check for Azure Service Bus (azureservicebus://)
                elif broker_url.startswith("azureservicebus://"):
                    config_info["broker_type"] = "Azure Service Bus"
                # Check for memory/testing broker (memory://)
                elif broker_url.startswith("memory://"):
                    config_info["broker_type"] = "In-Memory"
                else:
                    config_info["broker_type"] = "Other"

            # Get result backend
            result_backend = self.app.conf.get("result_backend", "")
            config_info["result_backend"] = result_backend

            if result_backend:
                # Check for Redis backend (redis://, rediss://, redis+socket://)
                if result_backend.startswith(
                    ("redis://", "rediss://", "redis+socket://")
                ):
                    config_info["result_backend_type"] = "Redis"
                # Check for database backends (db+, django-db, django-cache)
                elif result_backend.startswith("db+") or result_backend in (
                    "django-db",
                    "django-cache",
                ):
                    config_info["result_backend_type"] = "Database"
                # Check for MongoDB (mongodb://)
                elif result_backend.startswith("mongodb://"):
                    config_info["result_backend_type"] = "MongoDB"
                # Check for cache backends (cache+)
                elif result_backend.startswith("cache+"):
                    config_info["result_backend_type"] = "Cache"
                # Check for RPC backend (rpc://)
                elif result_backend.startswith("rpc://"):
                    config_info["result_backend_type"] = "RPC"
                # Check for S3 backend (s3://)
                elif result_backend.startswith("s3://"):
                    config_info["result_backend_type"] = "Amazon S3"
                # Check for filesystem backend (file://)
                elif result_backend.startswith("file://"):
                    config_info["result_backend_type"] = "Filesystem"
                # Check for disabled backend
                elif result_backend in ("disabled", "rpc"):
                    config_info["result_backend_type"] = "Disabled"
                else:
                    config_info["result_backend_type"] = "Other"

            # Basic configuration
            config_info["timezone"] = self.app.conf.get("timezone", "UTC")
            config_info["task_serializer"] = self.app.conf.get(
                "task_serializer", "json"
            )
            config_info["result_serializer"] = self.app.conf.get(
                "result_serializer", "json"
            )
            config_info["accept_content"] = self.app.conf.get(
                "accept_content", ["json"]
            )

            # Task execution settings
            config_info["task_acks_late"] = self.app.conf.get("task_acks_late", False)
            config_info["task_track_started"] = self.app.conf.get(
                "task_track_started", False
            )
            config_info["task_time_limit"] = self.app.conf.get("task_time_limit")
            config_info["task_soft_time_limit"] = self.app.conf.get(
                "task_soft_time_limit"
            )
            config_info["task_ignore_result"] = self.app.conf.get(
                "task_ignore_result", False
            )
            config_info["task_always_eager"] = self.app.conf.get(
                "task_always_eager", False
            )

            # Queue settings
            config_info["create_missing_queues"] = self.app.conf.get(
                "task_create_missing_queues", True
            )
            config_info["default_queue"] = self.app.conf.get(
                "task_default_queue", "celery"
            )
            config_info["default_exchange"] = self.app.conf.get(
                "task_default_exchange", ""
            )
            config_info["default_routing_key"] = self.app.conf.get(
                "task_default_routing_key", ""
            )

            # Worker settings
            config_info["worker_prefetch_multiplier"] = self.app.conf.get(
                "worker_prefetch_multiplier", 4
            )
            config_info["worker_max_tasks_per_child"] = self.app.conf.get(
                "worker_max_tasks_per_child"
            )

            # Result settings
            result_expires = self.app.conf.get("result_expires")
            if result_expires is not None:
                # Convert to human-readable format if it's in seconds
                if isinstance(result_expires, int):
                    if result_expires >= 86400:
                        config_info["result_expires"] = (
                            f"{result_expires // 86400} days"
                        )
                    elif result_expires >= 3600:
                        config_info["result_expires"] = (
                            f"{result_expires // 3600} hours"
                        )
                    elif result_expires >= 60:
                        config_info["result_expires"] = (
                            f"{result_expires // 60} minutes"
                        )
                    else:
                        config_info["result_expires"] = f"{result_expires} seconds"
                else:
                    config_info["result_expires"] = str(result_expires)

        except Exception:
            # If we can't get config info, just return empty values
            pass

        return config_info

    def get_status(self):
        """
        Get overall Celery status including workers and basic metrics.
        Returns a dictionary with stats suitable for display on the index page.

        This method uses a single stats() call to minimize broker round-trips
        and avoid fan-out issues with multiple blocking calls. This makes it
        suitable for synchronous request handling without causing timeouts.
        """
        status = {
            "celery_available": False,
            "workers": [],
            "workers_detail": [],  # Detailed worker information for table
            "active_workers_count": 0,
            "registered_tasks_count": 0,
            "active_tasks_count": None,  # Not available in lightweight mode
            "scheduled_tasks_count": None,  # Not available in lightweight mode
            "reserved_tasks_count": None,  # Not available in lightweight mode
            "error": None,
            "message": None,
            "config": {},
        }

        try:
            # Get configuration information (doesn't require broker connection)
            status["config"] = self.get_configuration_info()

            # Use a single stats() call to get worker information efficiently
            # This avoids multiple fan-out calls (active(), reserved(), scheduled())
            # that can cause performance issues and timeouts
            inspect = self.app.control.inspect()
            worker_stats = inspect.stats()

            if worker_stats is None:
                status["error"] = "No workers are currently running"
                return status

            status["celery_available"] = True
            status["workers"] = list(worker_stats.keys())
            status["active_workers_count"] = len(worker_stats)

            # Extract detailed worker information from stats
            workers_detail = []
            for worker_name, stats in worker_stats.items():
                worker_info = {
                    "name": worker_name,
                    "status": "online",
                    "pool": stats.get("pool", {}).get("implementation", "N/A"),
                    "concurrency": stats.get("pool", {}).get("max-concurrency", "N/A"),
                    "prefetch_count": stats.get("prefetch_count", "N/A"),
                    "total_tasks": stats.get("total", {}).values()
                    if isinstance(stats.get("total"), dict)
                    else [],
                    "pid": stats.get("pid", "N/A"),
                    "clock": stats.get("clock", "N/A"),
                    "rusage": stats.get("rusage", {}),
                }

                # Calculate total tasks executed (sum of all task counts)
                if isinstance(stats.get("total"), dict):
                    worker_info["total_tasks_executed"] = sum(
                        stats.get("total", {}).values()
                    )
                else:
                    worker_info["total_tasks_executed"] = 0

                workers_detail.append(worker_info)

            status["workers_detail"] = workers_detail

            # Count registered tasks (this is a local operation, not a broker call)
            status["registered_tasks_count"] = len(list(self.app.tasks.keys()))

            # Note: Real-time task counts (active/scheduled/reserved) are intentionally
            # not included to keep this method lightweight. Each of those would require
            # an additional broadcast to all workers.
            #
            # For detailed task metrics, consider:
            # 1. Using Celery's event system with a persistent monitor
            # 2. Caching results from periodic background polling
            # 3. Using a time-series database to track worker metrics

        except Exception as e:
            status["error"] = f"Error connecting to Celery: {str(e)}"
            # Still try to get config info even if broker connection fails
            try:
                status["config"] = self.get_configuration_info()
            except Exception:
                pass

        return status

    def get_registered_tasks(self, exclude_internal=True):
        """
        Get all registered tasks in the Celery app.

        Args:
            exclude_internal: bool - If True, filters out celery.* internal tasks

        Returns:
            list: List of task names
        """
        tasks = list(self.app.tasks.keys())
        if exclude_internal:
            tasks = [t for t in tasks if not t.startswith("celery.")]
        return tasks

    def get_periodic_tasks(self):
        """
        Get periodic tasks from the beat schedule.

        Returns:
            list: List of dicts containing periodic task information
        """
        periodic_tasks = []
        if hasattr(self.app.conf, "beat_schedule"):
            beat_schedule = self.app.conf.beat_schedule or {}
            for task_name, task_config in beat_schedule.items():
                periodic_tasks.append(
                    {
                        "name": task_name,
                        "task": task_config.get("task", "N/A"),
                        "schedule": str(task_config.get("schedule", "N/A")),
                        "args": task_config.get("args", []),
                        "kwargs": task_config.get("kwargs", {}),
                    }
                )
        return periodic_tasks

    def get_queues(self):
        """
        Get active task queues from all workers.

        Returns:
            dict: Dictionary with 'queues' list and optional 'error' message
        """
        result = {"queues": [], "error": None}

        try:
            inspect_obj = self.app.control.inspect()
            active_queues = inspect_obj.active_queues()

            if active_queues:
                # Collect unique queues across all workers
                queue_info = {}

                for worker, worker_queues in active_queues.items():
                    for queue in worker_queues:
                        queue_name = queue.get("name", "Unknown")

                        if queue_name not in queue_info:
                            queue_info[queue_name] = {
                                "name": queue_name,
                                "exchange": queue.get("exchange", {}).get(
                                    "name", "N/A"
                                ),
                                "routing_key": queue.get("routing_key", "N/A"),
                                "workers": [],
                            }

                        queue_info[queue_name]["workers"].append(worker)

                result["queues"] = list(queue_info.values())
        except Exception as e:
            result["error"] = str(e)

        return result

    def get_workers(self):
        pass

    def get_scheduled_tasks(self):
        pass

    def get_active_tasks(self):
        pass

    def get_task_history(self):
        pass

    def get_task_status(self):
        pass
