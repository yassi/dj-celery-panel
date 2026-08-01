from dj_control_room_base.core import PanelPlugin


class CeleryPanel(PanelPlugin):
    name = "Celery Panel"
    description = "Monitor Celery workers and task queues"
    icon = "chart"
    icon_color = "success"
    features = [
        "Browse registered tasks and periodic (beat) schedules",
        "Inspect active workers and their queues in real time",
        "Search task execution history with status filters",
        "Swap in custom backends for tasks, workers, and queues",
    ]

    app_name = "dj_celery_panel"
    docs_url = "https://github.com/django-control-room/dj-celery-panel"
    pypi_url = "https://pypi.org/project/dj-celery-panel/"

    def get_url_name(self):
        return "index"

    def get_config(self):
        from .conf import panel_config

        return panel_config
