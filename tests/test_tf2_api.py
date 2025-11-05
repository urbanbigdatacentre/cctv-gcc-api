import zoneinfo
from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from pytest_drf import (
    APIViewTest,
    Returns200,
    ReturnsPageNumberPagination,
    UsesGetMethod,
)
from pytest_lambda import lambda_fixture

camera_fields = [
    "id",
    "camera_details",
    "camera_pk",
    "camera_ref",
    "timestamp",
    "camera_ok",
    "model_name",
    "cars",
    "persons",
    "bicycles",
    "trucks",
    "motorcycles",
    "buses",
]


@pytest.mark.parametrize("has_date_after", (True, False))
@pytest.mark.parametrize("has_date_before", (True, False))
@pytest.mark.parametrize("date_format", ("%Y%m%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"))
class Test_TF2_Api_Camera_Records(APIViewTest, Returns200, UsesGetMethod, ReturnsPageNumberPagination):
    url = lambda_fixture(lambda: reverse("cctv-api:tf2:records-list"))

    @pytest.fixture
    def query_params(self, tf2records_model, has_date_before, has_date_after, date_format):
        camera_id = tf2records_model.objects.first().camera_id
        date_after: datetime = (
            tf2records_model.objects.filter(camera__id=camera_id).order_by("timestamp").first().timestamp
        )
        date_before: datetime = (
            tf2records_model.objects.filter(camera__id=camera_id).order_by("timestamp").last().timestamp
        )
        return {
            "camera_id": camera_id,
            "date_after": date_after.strftime(date_format) if has_date_after else "",
            "date_before": date_before.strftime(date_format) if has_date_before else "",
        }

    def test_result(self, url, query_params, date_format, results: dict):
        assert len(results) > 0
        camera_id: str = query_params["camera_id"]
        date_after: str = query_params["date_after"]
        date_before: str = query_params["date_before"]
        for r in results:
            for expected_field in camera_fields:
                assert expected_field in r
            assert r["camera_pk"] == camera_id
            assert r["timestamp"]
            if date_after:
                date_after_dt = datetime.strptime(date_after, date_format).replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                target_date: datetime = parse_datetime(r["timestamp"])  # type: ignore
                target_date.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                assert date_after_dt.date() <= target_date.date(), (
                    "dates should be greater than or equal to the date after: {} <= {}".format(
                        date_after_dt.date(),
                        target_date.date(),
                    )
                )
            if date_before:
                date_before_dt = datetime.strptime(date_before, date_format).replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                date_after_dt = date_before_dt + timedelta(days=1)
                target_date: datetime = parse_datetime(r["timestamp"])  # type: ignore
                target_date.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                assert date_before_dt.date() >= target_date.date(), (
                    "dates should be less than to the date before: {} >= {}".format(
                        date_before_dt.date(),
                        target_date.date(),
                    )
                )
