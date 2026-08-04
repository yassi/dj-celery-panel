from datetime import timedelta

from celery import Celery
from django.test import SimpleTestCase

from dj_celery_panel.celery_utils.inspector import (
    CeleryInspector,
    classify_broker_type,
    classify_result_backend_type,
    format_result_expires,
)


class TestClassifyBrokerType(SimpleTestCase):
    """Unit tests for classify_broker_type."""

    def test_empty_and_none(self):
        self.assertIsNone(classify_broker_type(""))
        self.assertIsNone(classify_broker_type(None))

    def test_redis_variants(self):
        self.assertEqual(classify_broker_type("redis://localhost:6379/0"), "Redis")
        self.assertEqual(classify_broker_type("rediss://localhost:6379/0"), "Redis")
        self.assertEqual(
            classify_broker_type("redis+socket:///tmp/redis.sock"), "Redis"
        )

    def test_amqp_variants(self):
        self.assertEqual(
            classify_broker_type("amqp://guest@localhost//"), "RabbitMQ (AMQP)"
        )
        self.assertEqual(
            classify_broker_type("amqps://guest@localhost//"), "RabbitMQ (AMQP)"
        )
        self.assertEqual(
            classify_broker_type("pyamqp://guest@localhost//"), "RabbitMQ (AMQP)"
        )
        self.assertEqual(
            classify_broker_type("librabbitmq://guest@localhost//"), "RabbitMQ (AMQP)"
        )

    def test_sqs_variants(self):
        self.assertEqual(classify_broker_type("sqs://"), "Amazon SQS")
        self.assertEqual(classify_broker_type("sqss://"), "Amazon SQS")

    def test_other_known_brokers(self):
        self.assertEqual(classify_broker_type("mongodb://localhost/celery"), "MongoDB")
        self.assertEqual(classify_broker_type("kafka://localhost:9092"), "Apache Kafka")
        self.assertEqual(
            classify_broker_type("azureservicebus://..."), "Azure Service Bus"
        )
        self.assertEqual(classify_broker_type("memory://"), "In-Memory")

    def test_unknown_broker(self):
        self.assertEqual(classify_broker_type("custom://localhost"), "Other")
        self.assertEqual(classify_broker_type("not-a-url"), "Other")


class TestClassifyResultBackendType(SimpleTestCase):
    """Unit tests for classify_result_backend_type."""

    def test_empty_and_none(self):
        self.assertIsNone(classify_result_backend_type(""))
        self.assertIsNone(classify_result_backend_type(None))

    def test_redis_variants(self):
        self.assertEqual(
            classify_result_backend_type("redis://localhost:6379/1"), "Redis"
        )
        self.assertEqual(
            classify_result_backend_type("rediss://localhost:6379/1"), "Redis"
        )
        self.assertEqual(
            classify_result_backend_type("redis+socket:///tmp/redis.sock"), "Redis"
        )

    def test_database_variants(self):
        self.assertEqual(classify_result_backend_type("django-db"), "Database")
        self.assertEqual(classify_result_backend_type("django-cache"), "Database")
        self.assertEqual(
            classify_result_backend_type("db+postgresql://user@localhost/db"),
            "Database",
        )

    def test_other_known_backends(self):
        self.assertEqual(
            classify_result_backend_type("mongodb://localhost/results"), "MongoDB"
        )
        self.assertEqual(
            classify_result_backend_type("cache+memcached://localhost:11211/"), "Cache"
        )
        self.assertEqual(classify_result_backend_type("rpc://"), "RPC")
        self.assertEqual(
            classify_result_backend_type("s3://bucket/results"), "Amazon S3"
        )
        self.assertEqual(
            classify_result_backend_type("file:///var/celery/results"), "Filesystem"
        )

    def test_disabled_variants(self):
        # Exact "rpc" (no scheme) is Disabled; "rpc://" is RPC.
        self.assertEqual(classify_result_backend_type("disabled"), "Disabled")
        self.assertEqual(classify_result_backend_type("rpc"), "Disabled")
        self.assertEqual(classify_result_backend_type("rpc://"), "RPC")

    def test_unknown_backend(self):
        self.assertEqual(classify_result_backend_type("custom://backend"), "Other")
        self.assertEqual(classify_result_backend_type("not-a-backend"), "Other")


class TestFormatResultExpires(SimpleTestCase):
    """Unit tests for format_result_expires."""

    def test_none(self):
        self.assertIsNone(format_result_expires(None))

    def test_days(self):
        self.assertEqual(format_result_expires(86400), "1 days")
        self.assertEqual(format_result_expires(172800), "2 days")

    def test_hours(self):
        self.assertEqual(format_result_expires(3600), "1 hours")
        self.assertEqual(format_result_expires(7200), "2 hours")
        # Just under a day still reports hours
        self.assertEqual(format_result_expires(86399), "23 hours")

    def test_minutes(self):
        self.assertEqual(format_result_expires(60), "1 minutes")
        self.assertEqual(format_result_expires(120), "2 minutes")
        # Just under an hour still reports minutes
        self.assertEqual(format_result_expires(3599), "59 minutes")

    def test_seconds(self):
        self.assertEqual(format_result_expires(1), "1 seconds")
        self.assertEqual(format_result_expires(59), "59 seconds")
        self.assertEqual(format_result_expires(0), "0 seconds")

    def test_non_int(self):
        self.assertEqual(format_result_expires(timedelta(days=1)), "1 day, 0:00:00")
        self.assertEqual(format_result_expires("1 day"), "1 day")


class TestGetConfigurationInfo(SimpleTestCase):
    """Integration-style tests that get_configuration_info wires the helpers."""

    def setUp(self):
        self.app = Celery("test_inspector_app")
        self.app.conf.update(
            broker_url="redis://localhost:6379/0",
            result_backend="django-db",
            result_expires=86400,
            timezone="UTC",
        )
        self.inspector = CeleryInspector(self.app)

    def test_classifies_broker_and_backend(self):
        config = self.inspector.get_configuration_info()

        self.assertEqual(config["broker_url"], "redis://localhost:6379/0")
        self.assertEqual(config["broker_type"], "Redis")
        self.assertEqual(config["result_backend"], "django-db")
        self.assertEqual(config["result_backend_type"], "Database")
        self.assertEqual(config["result_expires"], "1 days")

    def test_amqp_broker_and_rpc_backend(self):
        self.app.conf.update(
            broker_url="amqp://guest@localhost//",
            result_backend="rpc://",
            result_expires=90,
        )
        config = self.inspector.get_configuration_info()

        self.assertEqual(config["broker_type"], "RabbitMQ (AMQP)")
        self.assertEqual(config["result_backend_type"], "RPC")
        self.assertEqual(config["result_expires"], "1 minutes")

    def test_empty_broker_and_backend(self):
        self.app.conf.update(
            broker_url="",
            result_backend="",
            result_expires=None,
        )
        config = self.inspector.get_configuration_info()

        self.assertEqual(config["broker_url"], "")
        self.assertIsNone(config["broker_type"])
        self.assertEqual(config["result_backend"], "")
        self.assertIsNone(config["result_backend_type"])
        self.assertIsNone(config["result_expires"])

    def test_unknown_types_fall_back_to_other(self):
        self.app.conf.update(
            broker_url="custom-broker://host",
            result_backend="custom-backend://host",
            result_expires=30,
        )
        config = self.inspector.get_configuration_info()

        self.assertEqual(config["broker_type"], "Other")
        self.assertEqual(config["result_backend_type"], "Other")
        self.assertEqual(config["result_expires"], "30 seconds")
