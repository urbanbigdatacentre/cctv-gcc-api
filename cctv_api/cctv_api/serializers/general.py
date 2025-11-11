from zoneinfo import ZoneInfo

from rest_framework import serializers

from cctv_records.models import Cameras
from cctv_records.utils import get_cameras_that_have_records

UTC = ZoneInfo("UTC")


class VersionSerializer(serializers.Serializer):
    version = serializers.CharField()
    latest_data_update = serializers.DateTimeField()


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cameras
        # fields = "__all__"
        exclude = ["camera_id"]


class DateValueSerializer(serializers.Serializer):
    date = serializers.DateField(read_only=True, format="%Y-%m-%d")
    value = serializers.FloatField()
