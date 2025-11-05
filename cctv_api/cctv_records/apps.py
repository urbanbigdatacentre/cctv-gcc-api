from django.apps import AppConfig


class CCTVRecordsConfig(AppConfig):
    name = "cctv_records"

    def ready(self):
        from . import signals  # noqa
