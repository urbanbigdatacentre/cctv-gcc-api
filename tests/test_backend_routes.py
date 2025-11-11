from django.urls import reverse


def test_api_docs_routes():
    assert reverse("cctv-api:api-docs") == "/docs/"
    assert reverse("cctv-api:schema") == "/schema.yaml"


def test_maintenance_routes():
    assert reverse("cctv-records:upload-report") == "/upload_report"


def test_tf2_routes():
    assert reverse("cctv-api:tf2:records-list").startswith("/tf2/records")


def test_yolo_routes():
    assert reverse("cctv-api:yolo:records-list").startswith("/yolo/records")
