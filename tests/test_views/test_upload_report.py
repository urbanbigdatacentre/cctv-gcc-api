import pytest
from django.test import Client
from django.urls import reverse


client = Client()


@pytest.fixture
def upload_file():
    from pathlib import Path

    rv = Path(__file__).parent / "test_files" / "cctv-report-v2-tf2-20251029.csv.gz"
    assert rv.exists()
    return rv.open("rb")


@pytest.mark.django_db
def test_upload_report_view(upload_file):
    url = reverse("cctv-records:upload-report")
    response = client.post(url, {"file": upload_file})

    assert response.status_code == 401  # Unauthorized without authentication
    upload_file.seek(0)

    response = client.post(url, {"file": upload_file, "pin-code": "wrong-pin"})
    assert response.status_code == 401  # Unauthorized with wrong pin
    upload_file.seek(0)

    response = client.post(url, data={"file": upload_file, "pin-code": "123"})
    assert response.status_code == 200
