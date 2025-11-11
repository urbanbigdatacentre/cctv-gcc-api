import pytest


@pytest.fixture(scope="function", autouse=True)
def _auto_prov_db(provision_db):
    """Auto provision the test database."""
    pass


@pytest.mark.django_db
def test_camera_serializer(camera_model):
    from cctv_api.serializers.general import CameraSerializer

    cmra = camera_model.objects.first()
    serializer = CameraSerializer(cmra)
    assert serializer.data
    assert "groups" not in serializer.data


@pytest.mark.django_db
def test_tf2_serialiser(tf2records_model):
    from cctv_api.serializers.tf2 import TF2RecordSerialzer

    rcd = tf2records_model.objects.first()
    serializer = TF2RecordSerialzer(
        rcd,
    )
    assert serializer.data
    assert "timestamp" in serializer.data
    assert "camera_detail" in serializer.data
    assert not serializer.data.__contains__("camera_ref")


@pytest.mark.django_db
def test_yolo_serialiser(yolorecords_model, rf):
    from cctv_api.serializers.yolo import YOLORecordSerialzer

    rcd = yolorecords_model.objects.first()
    request = rf.get("/")
    serializer = YOLORecordSerialzer(rcd, context={"request": request})
    assert serializer.data
    assert "timestamp" in serializer.data
    assert "camera_detail" in serializer.data
    assert not serializer.data.__contains__("camera_ref")
