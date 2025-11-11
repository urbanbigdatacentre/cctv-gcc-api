import typing as t
from zoneinfo import ZoneInfo

from rest_framework import serializers

from cctv_records.models import CameraGroups, Cameras
from cctv_records.utils import get_cameras_that_have_records

UTC = ZoneInfo("UTC")

if t.TYPE_CHECKING:
    from cctv_records.models import CameraGroups


class VersionSerializer(serializers.Serializer):
    version = serializers.CharField()
    latest_data_update = serializers.DateTimeField()


class CameraGroupAttributeField(serializers.RelatedField):
    def to_representation(self, value: "CameraGroups"):
        return {"id": value.pk, "name": value.name}


class CameraGroupSerializer(serializers.ModelSerializer):
    camera_ids = serializers.SerializerMethodField()

    def get_camera_ids(self, obj):
        c = get_cameras_that_have_records(group=obj)
        return [x.pk for x in c]

    class Meta:
        model = CameraGroups
        fields = "__all__"


class CameraSerializer(serializers.ModelSerializer):
    groups = CameraGroupAttributeField(many=True, read_only=True)

    class Meta:
        model = Cameras
        # fields = "__all__"
        exclude = ["camera_id"]


class DateValueSerializer(serializers.Serializer):
    date = serializers.DateField(read_only=True, format="%Y-%m-%d")
    value = serializers.FloatField()
