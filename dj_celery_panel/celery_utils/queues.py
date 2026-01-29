import json
from dataclasses import dataclass
from typing import Optional

from .base import CeleryAbstractInterface
from .inspector import CeleryInspector


@dataclass(frozen=True)
class QueueListPage:
    """Return type for queue list queries."""

    queues: list[dict]
    error: Optional[str] = None


@dataclass(frozen=True)
class QueueDetailPage:
    """Return type for single queue detail queries."""

    queue: Optional[dict]
    error: Optional[str] = None


class CeleryQueuesInterface(CeleryAbstractInterface):
    """
    Interface for retrieving queue information (both lists and individual queues).
    """

    BACKEND_KEY = "queues_backend"
    DEFAULT_BACKEND = "dj_celery_panel.celery_utils.CeleryQueuesInspectBackend"

    def get_queues(self) -> QueueListPage:
        """Get a list of all active queues."""
        return self.backend.get_queues()

    def get_queue_detail(self, queue_name: str) -> QueueDetailPage:
        """Get detailed information about a single queue."""
        return self.backend.get_queue_detail(queue_name)


class CeleryQueuesInspectBackend:
    """Backend for retrieving queue information from Celery inspect API."""

    BACKEND_DESCRIPTION = "Queue bindings and routing configuration"
    DATA_SOURCE = "Celery Inspect API"

    def __init__(self, app):
        self.app = app
        self.inspector = CeleryInspector(app)

    def get_queues(self) -> QueueListPage:
        """Get active queues from worker inspection via CeleryInspector."""
        # Use the inspector's get_queues method which already handles
        # queue inspection using the active_queues() API
        result = self.inspector.get_queues()

        # Enhance each queue with message count from broker
        queues = result.get("queues", [])
        for queue in queues:
            broker_info = self._get_queue_length_from_broker(queue["name"])
            queue["message_count"] = broker_info.get("length")
            queue["broker_query_error"] = broker_info.get("error")

        return QueueListPage(queues=queues, error=result.get("error"))

    def _get_queue_length_from_broker(self, queue_name: str) -> dict:
        """
        Get queue length by querying the broker directly using Celery's connection API.
        Returns dict with 'length' (int or None) and 'error' (str or None).
        """
        result = {"length": None, "error": None}

        try:
            # Use Celery's connection API instead of manually parsing broker URLs
            # This is more backend-agnostic and handles all broker URL variations
            with self.app.connection_or_acquire() as conn:
                # Get the underlying client/transport
                transport = conn.transport
                transport_cls_name = transport.__class__.__name__

                # Check if this is a Redis-based broker
                if "redis" in transport_cls_name.lower():
                    try:
                        # Get the Redis client from Celery's connection
                        client = conn.channel().client

                        # Default queue key format in Celery with Redis
                        # Format is typically "celery" for default queue or the queue name
                        queue_key = queue_name

                        # Get the base queue length
                        length = client.llen(queue_key)

                        # Check if priority queues are enabled
                        # When using queue_order_strategy="priority", Celery creates
                        # multiple internal priority queues with keys like: queue_name + sep + priority
                        # We need to sum up all priority sub-queues
                        try:
                            channel = conn.default_channel

                            # Check if priority queues are being used
                            if (
                                hasattr(channel, "queue_order_strategy")
                                and channel.queue_order_strategy == "priority"
                            ):
                                # Get the separator and priority steps from the channel
                                # These can be customized in broker_transport_options
                                sep = getattr(channel, "sep", "\x06\x16")
                                priority_steps = getattr(
                                    channel, "priority_steps", [0, 3, 6, 9]
                                )

                                # Sum up lengths from all priority sub-queues
                                for priority in priority_steps:
                                    priority_queue_key = f"{queue_key}{sep}{priority}"
                                    length += client.llen(priority_queue_key)

                        except Exception:
                            # If we can't check for priority queues, just use the base length
                            # This ensures backward compatibility
                            pass

                        result["length"] = length

                    except ImportError:
                        result["error"] = "redis library not installed"
                    except Exception as e:
                        result["error"] = f"Redis error: {str(e)}"

                # Check if this is an AMQP-based broker (RabbitMQ, etc.)
                elif (
                    "amqp" in transport_cls_name.lower()
                    or "pyamqp" in transport_cls_name.lower()
                ):
                    try:
                        # Use Celery's connection to get a channel
                        channel = conn.channel()

                        # Passive declare to get queue info without creating it
                        # Returns (queue_name, message_count, consumer_count)
                        name, message_count, consumer_count = channel.queue_declare(
                            queue=queue_name, passive=True
                        )

                        result["length"] = message_count
                        result["consumer_count"] = consumer_count

                    except ImportError:
                        result["error"] = "amqp library not installed"
                    except Exception as e:
                        result["error"] = f"AMQP error: {str(e)}"
                else:
                    result["error"] = (
                        f"Unsupported broker type for queue length inspection: {transport_cls_name}"
                    )

        except Exception as e:
            result["error"] = f"Error querying broker: {str(e)}"

        return result

    def get_queue_detail(self, queue_name: str) -> QueueDetailPage:
        """Get detailed information about a single queue."""
        try:
            # Get all queues from all workers
            inspect_obj = self.app.control.inspect()
            active_queues_result = inspect_obj.active_queues()

            if not active_queues_result:
                return QueueDetailPage(
                    queue=None,
                    error="No workers are currently running",
                )

            # Find all workers that have this queue
            queue_detail = {
                "name": queue_name,
                "exchange": None,
                "exchange_type": None,
                "routing_key": None,
                "durable": None,
                "auto_delete": None,
                "exclusive": None,
                "arguments": None,
                "workers": [],
                "worker_details": [],
            }

            found = False

            for worker_name, worker_queues in active_queues_result.items():
                for queue in worker_queues:
                    if queue.get("name") == queue_name:
                        found = True

                        # Set queue properties (using first occurrence)
                        if queue_detail["exchange"] is None:
                            exchange = queue.get("exchange", {})
                            queue_detail["exchange"] = exchange.get("name", "N/A")
                            queue_detail["exchange_type"] = exchange.get("type", "N/A")
                            queue_detail["routing_key"] = queue.get(
                                "routing_key", "N/A"
                            )
                            queue_detail["durable"] = exchange.get("durable", False)
                            queue_detail["auto_delete"] = exchange.get(
                                "auto_delete", False
                            )
                            queue_detail["exclusive"] = queue.get("exclusive", False)
                            queue_detail["arguments"] = exchange.get("arguments", {})

                        # Add worker to the list
                        queue_detail["workers"].append(worker_name)

                        # Add detailed worker information
                        worker_info = {
                            "name": worker_name,
                            "queue_config": queue,
                        }
                        queue_detail["worker_details"].append(worker_info)

            if not found:
                return QueueDetailPage(
                    queue=None,
                    error=f"Queue '{queue_name}' not found in any active workers",
                )

            # Get queue length from broker
            broker_info = self._get_queue_length_from_broker(queue_name)
            queue_detail["message_count"] = broker_info.get("length")
            queue_detail["consumer_count"] = broker_info.get("consumer_count")
            queue_detail["broker_query_error"] = broker_info.get("error")

            # Format complex data as JSON
            queue_detail["exchange_json"] = json.dumps(
                {
                    "name": queue_detail["exchange"],
                    "type": queue_detail["exchange_type"],
                    "durable": queue_detail["durable"],
                    "auto_delete": queue_detail["auto_delete"],
                    "arguments": queue_detail["arguments"],
                },
                indent=2,
                default=str,
            )

            queue_detail["worker_configs_json"] = json.dumps(
                [wd["queue_config"] for wd in queue_detail["worker_details"]],
                indent=2,
                default=str,
            )

            return QueueDetailPage(queue=queue_detail)

        except Exception as e:
            return QueueDetailPage(
                queue=None, error=f"Error retrieving queue details: {str(e)}"
            )
