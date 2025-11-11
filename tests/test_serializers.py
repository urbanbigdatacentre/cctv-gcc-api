import pytest


@pytest.mark.django_db
def test_camera_serializer(camera_model):
    from cctv_api.serializers.general import CameraSerializer

    cmra = camera_model.objects.first()
    serializer = CameraSerializer(cmra)
    assert serializer.data
    assert "groups" not in serializer.data


def test_tf2_serialiser(tf2records_model):
    from cctv_api.serializers.tf2 import TF2RecordSerialzer

    rcd = tf2records_model.objects.first()
    serializer = TF2RecordSerialzer(rcd)
    assert serializer.data
    assert "timestamp" in serializer.data
    assert "camera_details" in serializer.data
    assert "camera_ref" in serializer.data
    assert serializer.data["camera_ref"] == rcd.camera.camera_id
    assert serializer.data["camera_pk"] == rcd.camera.id
    assert serializer.data["camera_details"].endswith(str(rcd.camera.id))


def test_yolo_serialiser(yolorecords_model):
    from cctv_api.serializers.yolo import YOLORecordSerialzer

    rcd = yolorecords_model.objects.first()
    serializer = YOLORecordSerialzer(rcd)
    assert serializer.data
    assert "timestamp" in serializer.data
    assert "camera_details" in serializer.data
    assert "camera_ref" in serializer.data
    assert serializer.data["camera_ref"] == rcd.camera.camera_id
    assert serializer.data["camera_pk"] == rcd.camera.id
    assert serializer.data["camera_details"].endswith(str(rcd.camera.id))
