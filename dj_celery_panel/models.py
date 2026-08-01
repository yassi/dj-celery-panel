from dj_control_room_base.core import PanelPlaceholderModel


class CeleryPanelPlaceholder(PanelPlaceholderModel):
    """
    This is a fake model used to create an entry in the admin panel for celery panel.
    When we register this app with the admin site, it is configured to simply load
    the celery panel templates.
    """

    class Meta(PanelPlaceholderModel.Meta):
        verbose_name = "DJ Celery Panel"
        verbose_name_plural = "DJ Celery Panel"
