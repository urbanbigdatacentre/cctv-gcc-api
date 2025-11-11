import pytest


@pytest.fixture()
def camera_model():
    """Return the Camera model class."""
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.Cameras")


@pytest.fixture()
def tf2records_model():
    """Return the CameraRecords model class."""
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.TF2Records")


@pytest.fixture()
def yolorecords_model():
    """Return the CameraRecords model class."""
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.YOLORecords")


@pytest.fixture(scope="function")
def camerarecordsfile_model():
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.CameraRecordsFile")


@pytest.fixture(scope="function")
def records_filter_model():
    """Return the CameraRanges model class."""
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.RecordsFilter")


@pytest.fixture(scope="session")
def api_client():
    """Return a RequestsClient instance."""
    from rest_framework.test import RequestsClient

    client = RequestsClient()
    return client

@pytest.fixture
def provision_db(camera_model, tf2records_model, yolorecords_model):
    """ Provision the test database with fake data """

    c_enabled = camera_model.objects.create(
        camera_id = "c_enabled",
        label = "Enabled Camera",
        longitude = 10.0,
        latitude = 20.0,
        is_complete = True,
    )
    c_disabled = camera_model.objects.create(
        camera_id = "c_disabled",
        label = "Disabled Camera",
    )

    for c in [c_enabled, c_disabled]:
        for i in range(5):
            tf2records_model.objects.create(
                camera=c,
                timestamp=f"2024-01-01T12:00:0{i}Z",

            )
            yolorecords_model.objects.create(
                camera=c,
                timestamp=f"2024-01-01T12:00:0{i}Z",
            )