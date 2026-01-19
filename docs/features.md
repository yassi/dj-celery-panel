# Features

Django Celery Panel provides a comprehensive monitoring and inspection interface for your Celery infrastructure, fully integrated into the Django admin.

## Overview

![Dashboard Overview](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/overview.png)

The **Overview** page provides a comprehensive dashboard of your entire Celery infrastructure at a glance. This is the landing page when you access Django Celery Panel.

### What You See:

- **Active Workers Summary**: Quick count of online workers
- **Recent Task Activity**: Summary of recent task executions
- **Queue Status**: Overview of configured queues
- **Registered Tasks**: List of all available Celery tasks
- **Periodic Tasks**: Scheduled tasks from Celery Beat
- **Quick Navigation**: Easy access to detailed views

The overview page is designed for fast loading with minimal API calls, giving you instant access to the most important information about your Celery setup.

---

## Workers Monitoring

![Workers Monitoring](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/workers.png)

The **Workers** page provides real-time monitoring of all active Celery workers in your infrastructure.

### Features:

- **Worker Status**: See which workers are online/offline
- **Worker Name & Hostname**: Identify each worker uniquely
- **Pool Type**: View the worker pool implementation (prefork, gevent, solo, eventlet)
- **Concurrency**: See how many concurrent tasks each worker can handle
- **Active Tasks**: View currently executing tasks
- **Detailed Statistics**: Click on any worker to see comprehensive details

### Worker Detail View:

When you click on a worker, you get detailed information including:

- Process ID (PID)
- Prefetch count
- Total tasks executed
- Active, reserved, and scheduled tasks
- Registered tasks for that worker
- Active queues the worker is consuming from
- Worker processes list
- Resource usage statistics (CPU, memory)
- Broker connection information

This real-time data comes directly from Celery's inspect API, giving you an accurate view of your workers' current state.

---

## Task Management

![Task Management](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/tasks.png)

The **Tasks** page provides comprehensive task history and inspection capabilities.

### Features:

- **Task History**: Browse all executed tasks with pagination
- **Status Indicators**: Visual indicators for success, failure, pending, retry states
- **Search Functionality**: Search tasks by name, ID, or other criteria
- **Task Details**: View complete information about each task
- **Execution Timeline**: See when tasks started and completed
- **Result Inspection**: View task results or error messages

### Task Information Displayed:

- **Task ID**: Unique identifier for each task execution
- **Task Name**: The function/task that was executed
- **Status**: Current state (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
- **Arguments**: The args and kwargs passed to the task
- **Result**: Return value or exception information
- **Timestamp**: When the task was received and completed
- **Duration**: How long the task took to execute
- **Worker**: Which worker processed the task
- **Queue**: Which queue the task was routed to

### Task Detail View:

Click on any task to see:

- Full task arguments and keyword arguments (formatted JSON)
- Complete result or error message
- Full exception traceback for failed tasks
- Task metadata (retries, time limits, etc.)
- Worker and queue information
- Execution timestamps

This is powered by `django-celery-results`, which stores comprehensive task execution history in your Django database.

---

## Queue Management

The **Queues** page displays all configured Celery queues and their routing configuration.

### Features:

- **Queue List**: All queues defined in your Celery configuration
- **Exchange Information**: Exchange name, type, and routing keys
- **Queue Bindings**: How queues are bound to exchanges
- **Routing Details**: Understand how tasks are routed to queues
- **Active Queues**: See which queues are actively consumed by workers

### Queue Information:

- **Queue Name**: Identifier for the queue
- **Exchange**: The exchange the queue is bound to
- **Exchange Type**: Direct, topic, fanout, or headers
- **Routing Key**: The routing key pattern
- **Durability**: Whether the queue survives broker restarts
- **Consumer Count**: How many workers are consuming from the queue

This information helps you understand your task routing configuration and ensure messages are being delivered correctly.

---

## Configuration View

![Configuration](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/config.png)

The **Configuration** page displays your Celery runtime configuration and Django Celery Panel settings.

### What's Displayed:

#### Celery Configuration

- **Broker URL**: Your message broker connection string (credentials masked)
- **Result Backend**: Where task results are stored
- **Task Settings**:
  - Task serialization format (JSON, pickle, etc.)
  - Task compression settings
  - Task time limits and soft time limits
  - Task acknowledgment settings
- **Worker Settings**:
  - Worker pool type
  - Worker prefetch multiplier
  - Worker concurrency
- **Beat Settings**:
  - Scheduler class
  - Beat schedule configuration
  - Timezone settings
- **Queue Configuration**:
  - Default queue settings
  - Task routing rules
  - Queue priorities

#### Django Celery Panel Settings

- **Backend Classes**: Which backend implementations are being used
  - Tasks backend (e.g., DjangoCeleryResults)
  - Workers backend (e.g., InspectAPI)
  - Queues backend (e.g., InspectAPI)
- **Custom Settings**: Any custom configuration options

### Why This Matters:

The configuration page is invaluable for:

- **Debugging**: Understanding how Celery is configured
- **Documentation**: Having a live view of your settings
- **Troubleshooting**: Verifying that settings are correct
- **Onboarding**: Helping new team members understand the setup

All sensitive information (like passwords in broker URLs) is automatically masked for security.

---

## Periodic Tasks

The **Periodic Tasks** page shows all scheduled tasks configured in Celery Beat.

### Features:

- **Schedule Display**: See when each task runs (cron, interval, solar)
- **Task Name**: The task that gets executed
- **Last Run**: When the task last executed (if available)
- **Enabled Status**: Whether the task is currently active
- **Schedule Details**: Human-readable schedule description

### Schedule Types:

- **Interval**: Tasks that run every X seconds/minutes/hours/days
- **Crontab**: Tasks with cron-style schedules (e.g., "0 0 * * *" for daily at midnight)
- **Solar**: Tasks based on solar events (sunrise, sunset)

This gives you visibility into your automated background tasks and when they're scheduled to run.

---

## Admin Integration

![Admin Integration](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/admin_home.png)

Django Celery Panel integrates seamlessly into your Django admin interface.

### Integration Features:

- **Admin Section**: Appears as a dedicated section in your admin home
- **Consistent Styling**: Matches Django admin's look and feel
- **Staff-Only Access**: Uses Django's `@staff_member_required` decorator
- **Permission System**: Leverages Django's existing authentication
- **Navigation**: Easy navigation between different monitoring views
- **Breadcrumbs**: Clear navigation path in the admin interface

### No Database Impact:

Unlike many Django admin apps, Django Celery Panel:

- **No Models**: Doesn't define any Django models
- **No Migrations**: No database migrations to run
- **Read-Only**: Only reads data, doesn't modify Celery state
- **Lightweight**: Minimal impact on your application

---

## Real-Time Data

All data displayed in Django Celery Panel is **real-time** and comes from:

1. **Celery Inspect API**: For worker and queue information
2. **django-celery-results**: For task history and results
3. **Celery Configuration**: For settings and registered tasks
4. **Celery Beat Schedule**: For periodic task information

This means you always see the current state of your Celery infrastructure, not cached or stale data.

---

## Use Cases

Django Celery Panel is perfect for:

### Development

- **Debugging Tasks**: See exactly what's happening with your tasks
- **Testing Queues**: Verify tasks are routed correctly
- **Worker Monitoring**: Ensure workers are picking up tasks

### Production

- **Operational Visibility**: Monitor your production Celery infrastructure
- **Troubleshooting**: Quickly identify failing tasks or offline workers
- **Performance Monitoring**: Track task execution times and throughput
- **Configuration Verification**: Confirm settings are correct in production

### Team Collaboration

- **Shared View**: Everyone can see the same monitoring data
- **No Extra Tools**: Uses your existing Django admin
- **Access Control**: Leverages Django's permission system
- **Documentation**: Live view of how Celery is configured

---

## Next Steps

- [Installation Guide](installation.md) - Get started with Django Celery Panel
- [Configuration](configuration.md) - Customize the panel for your needs
- [Development](development.md) - Contribute or run tests locally
