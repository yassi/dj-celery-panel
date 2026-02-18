class CeleryPanel:
    id = "dj_celery_panel"
    name = "Celery Panel"
    description = "Monitor Celery workers and task queues"
    icon = "chart"

    def get_url_name(self):
        return "index"
