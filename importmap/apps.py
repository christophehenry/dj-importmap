from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImportmapConfig(AppConfig):
    name = "importmap"
    verbose_name = _("HTML importmap managment")
    importmaps = None

    def ready(self):
        from importmap.base import importmaps

        importmaps.reset()
