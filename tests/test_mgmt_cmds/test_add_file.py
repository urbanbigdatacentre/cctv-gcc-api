import pytest
from django.apps import apps
from io import StringIO

from django.core.management import call_command


@pytest.mark.parametrize(
    "file_path,model",
    [
        ("tests/test_mgmt_cmds/test_files/cctv-report-v2-tf2-20251029.csv.gz", "tf2"),
        ("tests/test_mgmt_cmds/test_files/cctv-report-v2-yolo-20251029.csv.gz", "yolo"),
    ],
)
@pytest.mark.django_db
def test_add_csv_file(file_path, model):
    if model == "tf2":
        model = apps.get_model("cctv_records", "TF2Records")
    elif model == "yolo":
        model = apps.get_model("cctv_records", "YOLORecords")

    out = StringIO()
    call_command("add_csv_file", file_path, stdout=out)
    assert model.objects.count() > 0
    total_count = model.objects.count()

    call_command("add_csv_file", file_path, stdout=out)
    assert model.objects.count() == total_count
