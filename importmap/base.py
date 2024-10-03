from copy import copy
from typing import Mapping

from django.templatetags.static import static
from django.utils.functional import keep_lazy_text
from django.utils.module_loading import import_string

IMPORTMAP_MODULE_NAME = "importmaps"


class ImportMaps(Mapping):
    def __init__(self):
        self._inner_reset()

    def __getitem__(self, key, /):
        if not self._is_populated:
            self.reset()

        return self._cached[key]

    def __len__(self):
        if not self._is_populated:
            self.reset()

        return len(self._cached)

    def __iter__(self):
        if not self._is_populated:
            self.reset()

        return iter(self._cached)

    def reset(self):
        from django.apps import apps
        from django.conf import settings

        self._inner_reset()

        module_path = getattr(settings, "ROOT_IMPORTMAPCONF", None)

        try:
            if not module_path:
                module_path, _ = settings.ROOT_URLCONF.rsplit(".", 1)
                module_path = f"{module_path}.{IMPORTMAP_MODULE_NAME}"

            self._global_importmap = import_string(f"{module_path}.{IMPORTMAP_MODULE_NAME}")
            self._cached = copy(self._global_importmap)
        except (ValueError, ImportError):
            pass

        for label, app_config in apps.app_configs.items():
            try:
                self._apps_importmaps[label] = import_string(
                    f"{app_config.module.__package__}.{IMPORTMAP_MODULE_NAME}.{IMPORTMAP_MODULE_NAME}"
                )
            except ImportError:
                continue

            self._cached.update(self._apps_importmaps[label])
            self._per_app_cached[label] = copy(self._global_importmap)
            self._per_app_cached[label].update(self._apps_importmaps[label])

        self._is_populated = True

    def get_for_app(self, applabel):
        return self._per_app_cached[applabel]

    def _inner_reset(self):
        self._is_populated = False
        self._global_importmap = {}
        self._apps_importmaps = {}
        self._cached = {}
        self._per_app_cached = {}


importmaps = ImportMaps()
static = keep_lazy_text(static)
