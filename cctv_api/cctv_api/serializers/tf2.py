from rest_framework import serializers
from rest_framework.reverse import reverse

from cctv_records.models import TF2Records


class TF2RecordSerialzer(serializers.ModelSerializer):
    camera_detail = serializers.SerializerMethodField(read_only=True)
    camera_pk = serializers.IntegerField(source="camera.id", read_only=True)
    # camera_ref = serializers.SlugRelatedField(source="camera", read_only=True, many=False, slug_field="camera_id")

    def get_camera_detail(self, obj):
        request = self.context.get("request")
        format = self.context.get("format")
        return reverse("cctv-api:general:cameras-detail", kwargs={"pk": obj.camera.pk}, request=request, format=format)

    class Meta:
        model = TF2Records
        exclude = ["camera"]
