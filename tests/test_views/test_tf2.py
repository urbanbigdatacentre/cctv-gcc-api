from operator import le
import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_tf2_records_list_view():
    client = Client()
    url = reverse("cctv-api:tf2:records-list")
    response = client.get(url)
    assert response.status_code == 200

    data = response.json()
    results = data.get("results", [])
    assert len(results) == 5
