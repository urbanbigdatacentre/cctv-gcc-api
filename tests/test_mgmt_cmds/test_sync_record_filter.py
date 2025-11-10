from math import exp
import pytest
from pyexcel import get_sheet


from django.core.management import call_command


def dt_from_isostring(string):
    from pendulum import parse

    return parse(string)


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


intervals = [
    ["2023-01-01T00:00:00Z", "2023-01-03T00:00:00"],
    ["2023-01-02T00:00:00Z", "2023-01-06T00:00:00Z"],
    ["2023-01-08T00:00:00Z", "2023-01-10T00:00:00Z"],
    ["2023-01-15T00:00:00+01:00", "2023-01-18T00:00:00Z"],
]
expected = [
    [dt_from_isostring("2023-01-01T00:00:00Z"), dt_from_isostring("2023-01-06T00:00:00Z")],
    [dt_from_isostring("2023-01-08T00:00:00Z"), dt_from_isostring("2023-01-10T00:00:00Z")],
    [dt_from_isostring("2023-01-14T23:00:00Z"), dt_from_isostring("2023-01-18T00:00:00Z")],
]


@pytest.mark.django_db
def test_sync_record_filters_command(tmp_path, _provision_camera_data, records_filter_model):
    output_file = tmp_path / "data" / "cameras.xlsx"

    call_command("sync_record_filter", "--file", output_file)
    # initial file should be created with no records
    assert output_file.exists()

    sheet = get_sheet(file_name=str(output_file), name_columns_by_row=0)
    assert sheet.colnames == ["camera_id", "model", "from_datetime", "to_datetime", "delete_mark"]
    assert len(sheet) == 0

    # add 4 records in the file
    for interval in intervals:
        sheet.row += ["cam_001", "tf2", interval[0], interval[1], ""]
    sheet.save_as(str(output_file))

    call_command("sync_record_filter", "--file", output_file)
    sheet = get_sheet(file_name=str(output_file), name_columns_by_row=0)
    assert len(sheet) == 4
    assert records_filter_model.objects.count() == 4
    exclusion_intervals = records_filter_model.get_exclusion_intervals(camera="cam_001", model_name="tf2")
    assert exclusion_intervals[0]["exclusion_intervals"] == expected

    # mark one record for deletion
    sheet[2, -1] = "1"
    sheet.save_as(str(output_file))
    call_command("sync_record_filter", "--file", output_file)
    sheet = get_sheet(file_name=str(output_file), name_columns_by_row=0)
    assert len(sheet) == 3
    assert records_filter_model.objects.count() == 3
    exclusion_intervals = records_filter_model.get_exclusion_intervals(camera="cam_001", model_name="tf2")
    assert exclusion_intervals[0]["exclusion_intervals"] == expected[:1] + expected[2:]

    assert output_file.stat().st_mode == 0o100666  # ensure file has 666 permissions
