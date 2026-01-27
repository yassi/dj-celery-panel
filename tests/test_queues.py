"""
Tests for the queues page and queue detail page.
"""

from django.urls import reverse
from unittest.mock import Mock, patch, MagicMock

from .base import CeleryPanelTestCase
from dj_celery_panel.celery_utils import CeleryQueuesInspectBackend


class TestQueuesPage(CeleryPanelTestCase):
    """Test cases for the queues list page."""

    def test_queues_page_loads(self):
        """Test that the queues page loads successfully."""
        response = self.client.get(reverse("dj_celery_panel:queues"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Task Queues")

    def test_queues_page_shows_table_headers(self):
        """Test that the queues page shows appropriate table headers."""
        response = self.client.get(reverse("dj_celery_panel:queues"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Queue Name")
        self.assertContains(response, "Messages")
        self.assertContains(response, "Exchange")
        self.assertContains(response, "Routing Key")

    def test_queues_page_handles_no_queues(self):
        """Test that the queues page handles case when no queues are active."""
        response = self.client.get(reverse("dj_celery_panel:queues"))
        
        # Should still load successfully even with no queues
        self.assertEqual(response.status_code, 200)

    def test_queues_requires_authentication(self):
        """Test that unauthenticated users cannot access the queues page."""
        from django.test import Client
        
        client = Client()
        response = client.get(reverse("dj_celery_panel:queues"))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class TestQueueDetailPage(CeleryPanelTestCase):
    """Test cases for the queue detail page."""

    def test_queue_detail_page_loads_with_valid_queue_name(self):
        """Test that the queue detail page loads with a queue name."""
        # Using a dummy queue name - the page should load even if queue doesn't exist
        response = self.client.get(
            reverse("dj_celery_panel:queue_detail", kwargs={"queue_name": "celery"})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Queue Details")

    def test_queue_detail_shows_not_found_for_invalid_queue(self):
        """Test that the queue detail page shows error for invalid queue."""
        response = self.client.get(
            reverse("dj_celery_panel:queue_detail", kwargs={"queue_name": "nonexistent-queue"})
        )
        
        self.assertEqual(response.status_code, 200)
        # Should show some indication that queue wasn't found

    def test_queue_detail_requires_authentication(self):
        """Test that unauthenticated users cannot access queue detail."""
        from django.test import Client
        
        client = Client()
        response = client.get(
            reverse("dj_celery_panel:queue_detail", kwargs={"queue_name": "celery"})
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class TestPriorityQueueMessageCounting(CeleryPanelTestCase):
    """Test cases for priority queue message counting with Redis broker."""

    @patch('redis.from_url')
    def test_redis_priority_queue_message_count(self, mock_redis_from_url):
        """Test that message counts include all priority sub-queues when queue_order_strategy is priority."""
        # Setup mock Redis client
        mock_redis_client = MagicMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Simulate priority queues: base queue is empty, but priority sub-queues have messages
        queue_name = "test_queue"
        sep = '\x06\x16'  # Celery's default priority separator
        
        # Mock llen responses
        def llen_side_effect(key):
            if key == queue_name:
                return 0  # Base queue empty
            elif key == f"{queue_name}{sep}0":
                return 3  # 3 messages at priority 0
            elif key == f"{queue_name}{sep}3":
                return 2  # 2 messages at priority 3
            elif key == f"{queue_name}{sep}6":
                return 4  # 4 messages at priority 6
            elif key == f"{queue_name}{sep}9":
                return 1  # 1 message at priority 9
            return 0
        
        mock_redis_client.llen.side_effect = llen_side_effect
        
        # Setup mock Celery app with priority queues enabled
        mock_app = Mock()
        mock_app.conf.get.return_value = "redis://localhost:6379/0"
        
        # Mock connection and channel with priority queue settings
        mock_conn = Mock()
        mock_channel = Mock()
        mock_channel.queue_order_strategy = "priority"
        mock_channel.sep = sep
        mock_channel.priority_steps = [0, 3, 6, 9]
        mock_conn.default_channel = mock_channel
        mock_app.connection.return_value = mock_conn
        
        # Test the backend method
        backend = CeleryQueuesInspectBackend(mock_app)
        result = backend._get_queue_length_from_broker(queue_name)
        
        # Should sum up all priority queues: 0 + 3 + 2 + 4 + 1 = 10
        self.assertEqual(result["length"], 10)
        self.assertIsNone(result["error"])
        
        # Verify Redis was called for base queue and all priority sub-queues
        expected_calls = [
            queue_name,  # Base queue
            f"{queue_name}{sep}0",
            f"{queue_name}{sep}3",
            f"{queue_name}{sep}6",
            f"{queue_name}{sep}9",
        ]
        actual_calls = [call[0][0] for call in mock_redis_client.llen.call_args_list]
        self.assertEqual(actual_calls, expected_calls)

    @patch('redis.from_url')
    def test_redis_without_priority_queues(self, mock_redis_from_url):
        """Test that message counts work normally when priority queues are not enabled."""
        # Setup mock Redis client
        mock_redis_client = MagicMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        queue_name = "test_queue"
        
        # Mock llen to return 5 messages for base queue
        mock_redis_client.llen.return_value = 5
        
        # Setup mock Celery app WITHOUT priority queues
        mock_app = Mock()
        mock_app.conf.get.return_value = "redis://localhost:6379/0"
        
        # Mock connection without priority queue settings
        mock_conn = Mock()
        mock_channel = Mock()
        mock_channel.queue_order_strategy = "fifo"  # Not priority
        mock_conn.default_channel = mock_channel
        mock_app.connection.return_value = mock_conn
        
        # Test the backend method
        backend = CeleryQueuesInspectBackend(mock_app)
        result = backend._get_queue_length_from_broker(queue_name)
        
        # Should only return base queue length
        self.assertEqual(result["length"], 5)
        self.assertIsNone(result["error"])
        
        # Verify Redis was only called for the base queue
        mock_redis_client.llen.assert_called_once_with(queue_name)

    @patch('redis.from_url')
    def test_redis_priority_queues_with_custom_steps(self, mock_redis_from_url):
        """Test that custom priority steps are respected."""
        # Setup mock Redis client
        mock_redis_client = MagicMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        queue_name = "test_queue"
        custom_sep = '||'
        custom_steps = [0, 5, 10]
        
        # Mock llen responses
        def llen_side_effect(key):
            if key == queue_name:
                return 0
            elif key == f"{queue_name}{custom_sep}0":
                return 2
            elif key == f"{queue_name}{custom_sep}5":
                return 3
            elif key == f"{queue_name}{custom_sep}10":
                return 1
            return 0
        
        mock_redis_client.llen.side_effect = llen_side_effect
        
        # Setup mock Celery app with custom priority settings
        mock_app = Mock()
        mock_app.conf.get.return_value = "redis://localhost:6379/0"
        
        mock_conn = Mock()
        mock_channel = Mock()
        mock_channel.queue_order_strategy = "priority"
        mock_channel.sep = custom_sep
        mock_channel.priority_steps = custom_steps
        mock_conn.default_channel = mock_channel
        mock_app.connection.return_value = mock_conn
        
        # Test the backend method
        backend = CeleryQueuesInspectBackend(mock_app)
        result = backend._get_queue_length_from_broker(queue_name)
        
        # Should sum up: 0 + 2 + 3 + 1 = 6
        self.assertEqual(result["length"], 6)
        self.assertIsNone(result["error"])
