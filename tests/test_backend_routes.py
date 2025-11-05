from django.urls import reverse


def test_api_docs_routes():
    assert reverse("cctv-api:api-docs") == "/api/docs"
    assert reverse("cctv-api:openapi-schema") == "/api/openapi.json"


def test_general_routes():
    assert reverse("cctv-api:general:api-version").startswith("/api/general/version")
    assert reverse("cctv-api:general:groups-list").startswith("/api/general/groups")
    assert reverse("cctv-api:general:cameras-list").startswith("/api/general/cameras")
    assert reverse("cctv-api:general:cameras-detail", kwargs={"pk": 1}).startswith("/api/general/cameras")
    assert reverse("cctv-api:general:groups-detail", kwargs={"pk": 1}).startswith("/api/general/group")


def test_tf2_routes():
    assert reverse("cctv-api:tf2:records-list").startswith("/api/tf2/records")


def test_yolo_routes():
    assert reverse("cctv-api:yolo:records-list").startswith("/api/yolo/records")
