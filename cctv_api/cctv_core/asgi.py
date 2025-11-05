import logging
import os

from django.core.asgi import get_asgi_application

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(asctime)s:%(name)s.%(funcName)s:%(lineno)d: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cctv_core.settings")

application = get_asgi_application()
