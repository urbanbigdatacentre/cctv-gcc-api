from django.db.models.query import QuerySet
from rest_framework import generics

from cctv_api.filters import YOLORecordsFilter
from cctv_api.serializers.yolo import YOLORecordSerialzer
from cctv_records.models import RecordsFilter, YOLORecords


class YOLORecordsViewSet(generics.ListAPIView):

    http_method_names = [
        "get",
        "options",
    ]

    def get_queryset(self) -> QuerySet:
        prohibited_dateranges = RecordsFilter.get_exclusion_intervals(model_name="yolo")

        queryset = YOLORecords.objects.filter(camera__is_complete=True)

        for interval_entry in prohibited_dateranges:
            camera_id = interval_entry["camera_id"]
            exclusion_intervals = interval_entry["exclusion_intervals"]
            for exclusion_interval in exclusion_intervals:
                starting_datetime = exclusion_interval[0]
                ending_datetime = exclusion_interval[1]
                queryset = queryset.exclude(camera_id=camera_id, timestamp__range=(starting_datetime, ending_datetime))

        return queryset

    serializer_class = YOLORecordSerialzer
    filterset_class = YOLORecordsFilter
