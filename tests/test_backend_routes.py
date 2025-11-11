from django.urls import reverse


def test_api_docs_routes():
    assert reverse("cctv-api:api-docs") == "/docs/"
    assert reverse("cctv-api:schema") == "/schema.yaml"


def test_general_routes():
    assert reverse("cctv-api:general:api-version").startswith("/api/general/version")
    assert reverse("cctv-api:general:cameras-list").startswith("/api/general/cameras")
    assert reverse("cctv-api:general:cameras-detail", kwargs={"pk": 1}).startswith("/api/general/cameras")


def test_tf2_routes():
    assert reverse("cctv-api:tf2:records-list").startswith("/tf2/records")


def test_yolo_routes():
    assert reverse("cctv-api:yolo:records-list").startswith("/yolo/records")
