import pytest
from django.test import Client
from django.urls import reverse


client = Client()


@pytest.mark.django_db
def test_general_cameras(camera_model):
    url = reverse("cctv-api:general:cameras-list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.json().__len__() == 1


@pytest.mark.django_db
def test_general_camera_detail(camera_model):
    camera = camera_model.objects.filter(camera_id="c_enabled").first()
    url = reverse("cctv-api:general:cameras-detail", args=[camera.pk])
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert not data.__contains__("camera_id")
    assert data.__contains__("id")
    assert data["id"] == camera.pk
    assert data["is_complete"] is True
    assert data["label"] == camera.label
    assert data["longitude"] == camera.longitude
    assert data["latitude"] == camera.latitude

    camera = camera_model.objects.filter(camera_id="c_disabled").first()
    url = reverse("cctv-api:general:cameras-detail", args=[camera.pk])
    response = client.get(url)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No Cameras matches the given query."
