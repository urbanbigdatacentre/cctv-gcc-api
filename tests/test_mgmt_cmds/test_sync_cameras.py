import pytest
from datetime import datetime

from django.core.management import call_command


@pytest.mark.django_db
@pytest.fixture
def _provision_camera_data():
    from django.apps import apps

    model = apps.get_model("cctv_records", "Cameras")

    model.objects.create(
        camera_id="cam_001",
        label="Main Entrance",
        longitude=-4.2518,
        latitude=55.8642,
    )
    model.objects.create(
        camera_id="cam_002",
        label="Parking Lot",
        longitude=-4.2520,
        latitude=55.8650,
    )


@pytest.mark.django_db
def test_sync_cameras_command(tmp_path, _provision_camera_data, camera_model):
    output_file = tmp_path / "data" / "cameras.xlsx"

    call_command("sync_cameras", "--file", output_file)

    assert output_file.exists()
    from pyexcel import get_sheet

    sheet = get_sheet(file_name=str(output_file), name_columns_by_row=0)
    assert sheet.colnames == ["camera_id", "label", "longitude", "latitude"]
    assert len(sheet) == 2
    assert sheet.row[0] == ["cam_001", "Main Entrance", -4.2518, 55.8642]
    assert sheet.row[1] == ["cam_002", "Parking Lot", -4.2520, 55.8650]

    from cctv_records.schemas.remote import TF2ReportRecord

    obs = TF2ReportRecord(
        image_proc=datetime.now(),
        image_capt=datetime.now(),
        camera_ref="cam_003",
        model_name="tf2",
        car=5,
        person=2,
        bicycle=1,
        motorcycle=0,
        bus=0,
        truck=0,
        warnings=None,
    )
    obs.to_db_record()
    cam = camera_model.objects.get(camera_id="cam_003")
    assert cam.is_complete is False
    assert cam.label == ""
    assert cam.longitude is None
    assert cam.latitude is None

    call_command("sync_cameras", "--file", output_file)
    sheet = get_sheet(file_name=str(output_file), name_columns_by_row=0)
    assert len(sheet) == 3
    assert sheet.row[2] == ["cam_003", "", "", ""]

    sheet[2, 1] = "Side Street"
    sheet[2, 2] = -4.2530
    sheet[2, 3] = "55.8660"
    sheet.save_as(str(output_file))

    call_command("sync_cameras", "--file", output_file)
    cam.refresh_from_db()

    assert cam.label == "Side Street"
    assert cam.longitude == -4.2530
    assert cam.latitude == 55.8660
    assert cam.is_complete is True
    assert camera_model.objects.count() == 3
