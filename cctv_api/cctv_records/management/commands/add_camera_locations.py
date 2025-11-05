import json
from pathlib import Path

from django.core.management.base import BaseCommand

from cctv_records.models import Cameras

geojson = Path(__file__).parent / "camera_locations.geojson"
dd = json.load(geojson.open())


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        results = {"added": 0, "updated": 0}
        for feature in dd.get("features"):
            longitude = feature["geometry"]["coordinates"][0]
            latitude = feature["geometry"]["coordinates"][1]
            camera_id: str = (feature["properties"]["camera-name"]).lower().replace(" ", "")
            label: str = feature["properties"].get("camera-label")
            if label is None:
                label = "no-label"
            c, created = Cameras.objects.update_or_create(
                camera_id=camera_id,
                defaults={"label": label, "longitude": longitude, "latitude": latitude},
            )
            if created:
                results["added"] += 1
            else:
                results["updated"] += 1

        print(results)
