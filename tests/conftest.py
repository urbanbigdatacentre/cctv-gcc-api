import pytest


@pytest.fixture()
def camera_model():
    """Return the Camera model class."""
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.Cameras")


@pytest.fixture()
def cameragroup_model():
    """Return the CameraGroups model class."""
    from django.apps import apps as django_apps

    return django_apps.get_model("cctv_records.CameraGroups")


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
