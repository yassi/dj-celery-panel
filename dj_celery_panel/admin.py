from django.contrib import admin

from dj_control_room_base.core import BasePanelAdmin

from .conf import panel_config
from .models import CeleryPanelPlaceholder


@admin.register(CeleryPanelPlaceholder)
class CeleryPanelPlaceholderAdmin(BasePanelAdmin):
    redirect_url_name = "dj_celery_panel:index"
    panel_config = panel_config
