[![Django Control Room Panel](https://img.shields.io/badge/Django%20Control%20Room-Panel-0c4b33?logo=django)](https://github.com/django-control-room/dj-control-room)
[![Tests](https://github.com/django-control-room/dj-celery-panel/actions/workflows/test.yml/badge.svg)](https://github.com/django-control-room/dj-celery-panel/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/django-control-room/dj-celery-panel/branch/main/graph/badge.svg)](https://codecov.io/gh/django-control-room/dj-celery-panel)
[![PyPI version](https://badge.fury.io/py/dj-celery-panel.svg)](https://badge.fury.io/py/dj-celery-panel)
[![Python versions](https://img.shields.io/pypi/pyversions/dj-celery-panel.svg)](https://pypi.org/project/dj-celery-panel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/dj-celery-panel.svg)](https://pypi.org/project/dj-celery-panel/)


# Django Celery Panel

DJ Celery Panel brings Celery monitoring directly into the Django Admin.

![DJ Celery Panel](https://raw.githubusercontent.com/django-control-room/dj-celery-panel/main/images/django-celery.png)

**Compatible with [dj-control-room](https://github.com/django-control-room/dj-control-room).** Register this panel in the Control Room to manage it from a centralized dashboard.

- **Official site:** [djangocontrolroom.com](https://djangocontrolroom.com)
- **Project repo:** [dj-control-room](https://github.com/django-control-room/dj-control-room)

## Docs

[https://django-control-room.github.io/dj-celery-panel/](https://django-control-room.github.io/dj-celery-panel/)

## Features

- **Workers Monitoring**: View active Celery workers, their status, pool type, and concurrency
- **Task Management**: Browse and inspect Celery tasks with detailed information
- **Queue Overview**: Monitor configured queues and their routing
- **Periodic Tasks**: View scheduled periodic tasks and their schedules
- **Real-time Inspection**: Live data from Celery's inspect API
- **Django Admin Integration**: Seamlessly integrated into your existing Django admin interface
- **Swappable Backends**: Pluggable architecture for custom data sources and monitoring integrations (see [Configuration](https://django-control-room.github.io/dj-celery-panel/configuration/))


## Requirements

- Python 3.9+
- Django 4.2+


## Screenshots

### Django Admin Integration

Seamlessly integrated into your Django admin interface. A new section for dj-celery-panel
will appear in the same places where your models appear.

**NOTE:** This application does not actually introduce any model or migrations.

![Admin Home](https://raw.githubusercontent.com/django-control-room/dj-celery-panel/main/images/admin_home.png)

### Dashboard Overview

Get a quick overview of your Celery infrastructure including active workers, recent tasks, and queue status.

![Dashboard Overview](https://raw.githubusercontent.com/django-control-room/dj-celery-panel/main/images/overview.png)

### Workers Monitoring

View all active Celery workers with detailed information about their status, pool type, concurrency, and processing capabilities.

![Workers](https://raw.githubusercontent.com/django-control-room/dj-celery-panel/main/images/workers.png)

### Task Management

Browse and inspect your Celery tasks with complete details including status, arguments, results, and execution time.

![Tasks](https://raw.githubusercontent.com/django-control-room/dj-celery-panel/main/images/tasks.png)

### Configuration

View your Celery configuration including broker settings, result backend, and other runtime parameters.

![Configuration](https://raw.githubusercontent.com/django-control-room/dj-celery-panel/main/images/config.png)


## Installation

```bash
pip install dj-celery-panel dj-control-room
```

Add it to `INSTALLED_APPS`, include its URLs, and migrate:

```python
INSTALLED_APPS = [
    # ...
    "dj_control_room_base",
    "dj_celery_panel",
    "dj_control_room",
    # ...
]
```

```python
urlpatterns = [
    path("admin/dj-control-room-base/", include("dj_control_room_base.urls")),
    path("admin/dj-celery-panel/", include("dj_celery_panel.urls")),
    path("admin/dj-control-room/", include("dj_control_room.urls")),
    path("admin/", admin.site.urls),
]
```

```bash
python manage.py migrate
```

Then visit `/admin/` and look for the "DJ CELERY PANEL" section.

**Note:** The panel requires at least one Celery worker to be running to display worker and queue information.

For the full walkthrough, settings reference (swappable backends, periodic tasks, CSS), and production recommendations, see the [Installation](https://django-control-room.github.io/dj-celery-panel/installation/) and [Configuration](https://django-control-room.github.io/dj-celery-panel/configuration/) docs. See [Scopes](https://django-control-room.github.io/dj-celery-panel/scopes/) for per-view permission scopes.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Development Setup

Want to contribute or set up the project for local development? See [docs/development.md](docs/development.md) for prerequisites, Docker/virtualenv setup, running the example project, and the test suite.
