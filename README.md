[![Tests](https://github.com/yassi/dj-celery-panel/actions/workflows/test.yml/badge.svg)](https://github.com/yassi/dj-celery-panel/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/yassi/dj-celery-panel/branch/main/graph/badge.svg)](https://codecov.io/gh/yassi/dj-celery-panel)
[![PyPI version](https://badge.fury.io/py/dj-celery-panel.svg)](https://badge.fury.io/py/dj-celery-panel)
[![Python versions](https://img.shields.io/pypi/pyversions/dj-celery-panel.svg)](https://pypi.org/project/dj-celery-panel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)




# Django Celery Panel

Your Celery task inspector inside the Django admin


## Docs

[https://yassi.github.io/dj-celery-panel/](https://yassi.github.io/dj-celery-panel/)

## Features

- **TBD**: View all configured cache backends from your `CACHES` setting


### Project Structure

```
dj-celery-panel/
├── dj_celery_panel/         # Main package
│   ├── templates/           # Django templates
│   ├── views.py             # Django views
│   └── urls.py              # URL patterns
├── example_project/         # Example Django project
├── tests/                   # Test suite
├── images/                  # Screenshots for README
└── requirements.txt         # Development dependencies
```

## Requirements

- Python 3.9+
- Django 4.2+



## Screenshots

### Django Admin Integration
Seamlessly integrated into your Django admin interface. A new section for dj-celery-panel
will appear in the same places where your models appear.

**NOTE:** This application does not actually introduce any model or migrations.

![Admin Home](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/admin_home.png)

### Caches Overview
Get a list of all your caches as well as the allowed capabilities for each cache

![Instance Overview](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/instance_list.png)

### Key Search

![Key Search](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/key_search.png)

### Key Edits/Adds

![Key Detail](https://raw.githubusercontent.com/yassi/dj-celery-panel/main/images/key_detail.png)


## Installation

### 1. Install the Package

```bash
pip install dj-celery-panel
```

### 2. Add to Django Settings

Add `dj_celery_panel` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dj_celery_panel',  # Add this line
    # ... your other apps
]
```

### 3. Configure Cache Instances

Django cache panel will use the `CACHES` setting normally defined in django projects

```python
CACHES = {
    ...
}
```

Additionally, you can also define some extra settings for extending or changing behavior
of the existing cache panels.

Note: these are advanced settings; the vast majority of django projects will not need to
define any of these

```python
DJ_CACHE_PANEL_SETTINGS = {
    # Optional: completely replace the default backend-to-panel mapping
    # "BACKEND_PANEL_MAP": {}
    #
    # Optional: extend or override specific backend-to-panel mappings
    # Panel classes can be specified as:
    #   - Simple class name (e.g., "RedisCachePanel") - for built-in panels
    #   - Full module path (e.g., "myapp.panels.CustomCachePanel") - for custom panels
    "BACKEND_PANEL_EXTENSIONS": {
        # Example: Map a custom backend to a custom panel class
        # "myapp.backends.CustomCache": "myapp.panels.CustomCachePanel",
        # Example: Override a built-in backend mapping
        # "django.core.cache.backends.redis.RedisCache": "myapp.panels.MyRedisCachePanel",
    },
    # Optional: per-cache settings overrides
    # Typically used to lock down a cache instance to only certain abilities
    "CACHES": {
        "redis": {
            "abilities": {  # Optional: override the abilities for this cache instance
                # "query": True,
                # "get_key": True,
                # "delete_key": True,
                # "edit_key": True,
                # "add_key": True,
                # "flush_cache": True,
            },
        }
    },
}
```




### 4. Include URLs

Add the Cache Panel URLs to your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/dj-celery-panel/', include('dj_celery_panel.urls')),  # Add this line
    path('admin/', admin.site.urls),
]
```

### 5. Run Migrations and Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser  # If you don't have an admin user
```

### 6. Access the Panel

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to the Django admin at `http://127.0.0.1:8000/admin/`

3. Look for the "DJ_CACHE_PANEL" section in the admin interface

4. Click "Manage Cache keys and values" to start browsing your cache instances



## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Development Setup

If you want to contribute to this project or set it up for local development:

### Prerequisites

- Python 3.9 or higher
- Redis server running locally
- Git
- Autoconf
- Docker

It is reccommended that you use docker since it will automate much of dev env setup

### 1. Clone the Repository

```bash
git clone https://github.com/yassi/dj-celery-panel.git
cd dj-celery-panel
```

### 2a. Set up dev environment using virtualenv

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -e . # install dj-celery-panel package locally
pip intall -r requirements.txt  # install all dev requirements

# Alternatively
make install # this will also do the above in one single command
```

### 2b. Set up dev environment using docker

```bash
make docker_up  # bring up all services (redis, memached) and dev environment container
make docker_shell  # open up a shell in the docker conatiner
```

### 3. Set Up Example Project

The repository includes an example Django project for development and testing

```bash
cd example_project
python manage.py migrate
python manage.py createsuperuser
```

### 4. Populate Test Data (Optional)
An optional CLI tool for populating cache keys automatically is included in the
example django project in this code base.

```bash
python manage.py populate_redis
```

This command will populate your cache instance with sample data for testing.

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to access the Django admin with Cache Panel.

### 7. Running Tests

The project includes a comprehensive test suite. You can run them by using make or
by invoking pytest directly:

```bash
# build and install all dev dependencies and run all tests inside of docker container
make test_docker

# Test without the docker on your host machine.
# note that testing always requires a redis and memcached service to be up.
# these are mostly easily brought up using docker
make test_local
```
