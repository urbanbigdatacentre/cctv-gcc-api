from pathlib import Path

camera_groups_fixture = Path(__file__).parent / "camera_groups.json"
camera_locations_fixture = Path(__file__).parent / "camera_locations.geojson"
assert camera_locations_fixture.exists()
