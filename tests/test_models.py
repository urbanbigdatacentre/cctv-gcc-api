import pytest


def dt_from_isostring(string):
    from datetime import datetime, timezone

    return datetime.fromisoformat(string).replace(tzinfo=timezone.utc)


@pytest.mark.django_db
def test_record_filter_ranges(camera_model, records_filter_model):
    """Test that the camera ranges model is created correctly"""
    intervals = [
        [dt_from_isostring("2023-01-01T00:00:00Z"), dt_from_isostring("2023-01-03T00:00:00")],
        [dt_from_isostring("2023-01-02T00:00:00Z"), dt_from_isostring("2023-01-06T00:00:00Z")],
        [dt_from_isostring("2023-01-08T00:00:00Z"), dt_from_isostring("2023-01-10T00:00:00Z")],
        [dt_from_isostring("2023-01-15T00:00:00+01:00"), dt_from_isostring("2023-01-18T00:00:00Z")],
    ]
    expected = [
        [dt_from_isostring("2023-01-01T00:00:00Z"), dt_from_isostring("2023-01-06T00:00:00Z")],
        [dt_from_isostring("2023-01-08T00:00:00Z"), dt_from_isostring("2023-01-10T00:00:00Z")],
        [dt_from_isostring("2023-01-15T00:00:00Z"), dt_from_isostring("2023-01-18T00:00:00Z")],
    ]
    a_camera = camera_model.create_camera(camera_id="q-11", longitude=0, latitude=0)
    for i in intervals:
        records_filter_model.objects.create(camera=a_camera, model="yolo", from_datetime=i[0], to_datetime=i[1])
    merged_intervals = a_camera.get_exclusion_intervals(model_name="yolo")
    assert merged_intervals == expected

    result = records_filter_model.get_exclusion_intervals(model_name="yolo")
    assert len(result) == 1
    assert "camera_id" in result[0].keys()
    assert "model" in result[0].keys()
    assert "exclusion_intervals" in result[0].keys()
    assert result[0]["exclusion_intervals"] == expected


@pytest.mark.django_db
def test_get_cameras_that_have_records(camera_model, tf2records_model, yolorecords_model):
    """Test that the get_cameras_that_have_records returns the correct number of cameras"""

    cam1 = camera_model.create_camera(camera_id="test_cam_1", longitude=0, latitude=0)
    camera_model.create_camera(camera_id="test_cam_2", longitude=0, latitude=0)
    tf2records_model.objects.create(camera=cam1, timestamp=dt_from_isostring("2023-01-01T00:00:00Z"))
    yolorecords_model.objects.create(camera=cam1, timestamp=dt_from_isostring("2023-01-02T00:00:00Z"))
    assert camera_model.objects.count() == 2

    from cctv_records.utils import get_cameras_that_have_records

    cams = get_cameras_that_have_records()
    assert cams.count() == 1
