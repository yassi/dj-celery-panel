from django.db import models


class CeleryPanelPlaceholder(models.Model):
    """
    This is a fake model used to create an entry in the admin panel for celery panel.
    When we register this app with the admin site, it is configured to simply load
    the celery panel templates.
    """

    class Meta:
        managed = False
        verbose_name = "DJ Celery Panel"
        verbose_name_plural = "DJ Celery Panel"
