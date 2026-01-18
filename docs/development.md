# Development

Contributing to Django Celery Panel or setting up for local development.

## Prerequisites

- Python 3.9+
- Git
- Docker (recommended)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/yassi/dj-celery-panel.git
cd dj-celery-panel
```

### 2. Choose Development Environment

#### Option A: Docker (Recommended)

```bash
make docker_up       # Start all services
make docker_shell    # Open shell in container
```

#### Option B: Local Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package and dependencies
make install
# or
pip install -e .
pip install -r requirements.txt
```

### 3. Set Up Example Project

```bash
cd example_project
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/admin/`

## Testing

The test suite requires a running instance of Celery with at least one worker, as well as Redis and PostgreSQL services. The tests verify the monitoring functionality against real Celery workers.

### Prerequisites for Tests

1. **Redis** - Running on `localhost:6379`
2. **PostgreSQL** - Running on `localhost:5432` (or use SQLite locally)
3. **Celery Worker** - At least one worker connected to the broker

### Run All Tests

#### Docker (Recommended)

```bash
# Docker automatically starts all required services including workers
make test_docker
```

#### Local Environment

```bash
# Terminal 1: Start Redis (if not already running)
docker run -d -p 6379:6379 redis:7

# Terminal 2: Start PostgreSQL (optional, or use SQLite)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16

# Terminal 3: Start Celery worker
cd example_project
python manage.py migrate
celery -A example_project worker --loglevel=info

# Terminal 4: Run tests
make test_local
```

### Run Specific Tests

```bash
pytest tests/test_admin.py -v
pytest tests/test_admin.py::TestAdminIntegration::test_celery_panel_appears_in_admin_index
```

### With Coverage

```bash
pytest --cov=dj_celery_panel tests/
```

### GitHub Actions

The CI pipeline automatically:
1. Starts Redis and PostgreSQL services
2. Runs database migrations
3. Starts a Celery worker in detached mode
4. Executes the test suite
5. Uploads coverage reports

## Project Structure

```
dj-celery-panel/
├── dj_celery_panel/          # Main package
│   ├── views.py              # Django views
│   ├── urls.py               # URL patterns
│   ├── models.py             # Placeholder model
│   ├── admin.py              # Admin integration
│   └── templates/            # HTML templates
├── tests/                    # Test suite
│   ├── base.py               # Test base class
│   ├── test_admin.py         # Admin integration tests
│   └── conftest.py           # Pytest configuration
├── example_project/          # Example Django project
├── docs/                     # Documentation
└── Makefile                  # Development commands
```

## Code Style

- Follow PEP 8
- Use type hints where helpful
- Write docstrings for public methods
- Keep functions focused and small

## Makefile Commands

```bash
make install        # Install dependencies
make test_local     # Run tests locally
make test_docker    # Run tests in Docker
make docker_up      # Start Docker services
make docker_down    # Stop Docker services
make docker_shell   # Open shell in container
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run test suite
6. Submit pull request
