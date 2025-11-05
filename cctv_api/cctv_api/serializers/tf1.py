from rest_framework import serializers

from cctv_records.models import TF1Records


class TF1RecordSerialzer(serializers.ModelSerializer):
    camera_pk = serializers.IntegerField(source="camera.id", read_only=True)
    camera_ref = serializers.SlugRelatedField(source="camera", read_only=True, many=False, slug_field="camera_id")

    class Meta:
        model = TF1Records
        # All fields except the camera field
        exclude = ["camera"]


class HistoricTF1RecordsSerializer(serializers.Serializer):
    aggregation = serializers.CharField()
    aggregation_method = serializers.CharField()
    date_after = serializers.DateTimeField()
    date_before = serializers.DateTimeField()
    object_types = serializers.ListField(child=serializers.CharField())
    camera_locations = serializers.ListField(child=serializers.IntegerField())
    records = serializers.ListField(child=serializers.DictField())
