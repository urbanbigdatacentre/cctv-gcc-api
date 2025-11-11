import pytest
from django.urls import is_valid_path, reverse


def dt_from_isostring(string):
    from datetime import datetime

    return datetime.fromisoformat(string)


@pytest.mark.parametrize(
    "intervals,expected",
    [
        ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
        (
            [
                [dt_from_isostring("2023-01-01T00:00:00"), dt_from_isostring("2023-01-03T00:00:00")],
                [dt_from_isostring("2023-01-02T00:00:00"), dt_from_isostring("2023-01-06T00:00:00")],
                [dt_from_isostring("2023-01-08T00:00:00"), dt_from_isostring("2023-01-10T00:00:00")],
                [dt_from_isostring("2023-01-15T00:00:00"), dt_from_isostring("2023-01-18T00:00:00")],
            ],
            [
                [dt_from_isostring("2023-01-01T00:00:00"), dt_from_isostring("2023-01-06T00:00:00")],
                [dt_from_isostring("2023-01-08T00:00:00"), dt_from_isostring("2023-01-10T00:00:00")],
                [dt_from_isostring("2023-01-15T00:00:00"), dt_from_isostring("2023-01-18T00:00:00")],
            ],
        ),
    ],
)
def test_merge_datetime_internal(intervals, expected):
    from cctv_records.helpers import merge_intervals

    result = merge_intervals(intervals)
    assert result == expected


