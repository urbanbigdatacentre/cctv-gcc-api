from django.db.models.query import QuerySet
from rest_framework import generics

from cctv_api.filters import TF2RecordsFilter
from cctv_api.serializers.tf2 import TF2RecordSerialzer
from cctv_records.models import RecordsFilter, TF2Records


class TF2RecordsViewSet(generics.ListAPIView):
    """
    ##  Tensorflow-v2 Records

    This endpoint provides a list of records from the Tensorflow-v2 model.
    The data are ordered by :
     - timestamp (descending)
     - camera_id (ascending)

    #### Parameters
    - page_size: The number of records to return per page. Default is 100. Max is 1000.
    - page: The page number to return. Default is 1.

    #### Note
    confidence level is set to 50%.
    """

    # schema = AutoSchema(tags=["tensorflow-v2"])
    http_method_names = [
        "get",
        "options",
    ]
    serializer_class = TF2RecordSerialzer
    filterset_class = TF2RecordsFilter

    def get_queryset(self) -> QuerySet:
        prohibited_dateranges = RecordsFilter.get_exclusion_intervals(model_name="tf2")

        queryset = TF2Records.objects.filter(camera__is_complete=True)

        for interval_entry in prohibited_dateranges:
            camera_id = interval_entry["camera_id"]
            exclusion_intervals = interval_entry["exclusion_intervals"]
            for exclusion_interval in exclusion_intervals:
                starting_datetime = exclusion_interval[0]
                ending_datetime = exclusion_interval[1]
                queryset = queryset.exclude(camera_id=camera_id, timestamp__range=(starting_datetime, ending_datetime))

        return queryset
