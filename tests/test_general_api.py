import pytest
from django.test import TestCase
from django.urls import reverse
from pytest_assert_utils import util
from pytest_drf import (
    APIViewTest,
    Returns200,
    ReturnsPageNumberPagination,
    UsesGetMethod,
)


class TestGeneralApi(TestCase):
    HTTP_ORIGIN = "https://glasgow-cctv.ubdc.ac.uk/"

    def is_cors_enabled_for_url(self, url):
        response = self.client.options(url, HTTP_ORIGIN=self.HTTP_ORIGIN)
        assert response.status_code == 200
        assert response["Access-Control-Allow-Origin"] == "*"
        assert response["Access-Control-Allow-Methods"] == "GET, OPTIONS"
        assert response["Access-Control-Max-Age"] == "86400"

    def test_cors_is_enabled_for_groups(self):
        url = reverse("cctv-api:general:groups-list")
        self.is_cors_enabled_for_url(url)


class TestCameraGroups(APIViewTest, UsesGetMethod, ReturnsPageNumberPagination, Returns200):
    @pytest.fixture
    def url(self):
        return reverse("cctv-api:general:groups-list")

    def test_camera_groups(self, json: dict):
        # 6 groups in total, 1 is hidden (default)
        assert json["count"] == 6 - 1


class TestCameras(APIViewTest, UsesGetMethod, Returns200):
    @pytest.fixture
    def url(self):
        return reverse("cctv-api:general:cameras-list")

    def test_result(self, json: dict):
        assert len(json) == 20
        first_record = json[0]
        assert first_record["groups"] == util.Any(list)
