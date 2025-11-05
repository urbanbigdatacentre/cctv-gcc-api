import typing as t
from datetime import datetime, timezone
from statistics import mean

from django.db.models import QuerySet, Subquery
from django.http import JsonResponse
from rest_framework import generics, views
from rest_framework.schemas.openapi import AutoSchema

from cctv_api.filters import TF1RecordFilter
from cctv_api.serializers.tf1 import HistoricTF1RecordsSerializer, TF1RecordSerialzer
from cctv_records.models import RecordsFilter, TF1Records
from cctv_records.utils import aggregate_records_qs, get_cameras_that_have_records

if t.TYPE_CHECKING:
    from rest_framework.request import Request


class TF1HistoricRecordsViewDetail(views.APIView):
    """
    ## Historic Records - Frontend Consumption
    """

    schema = AutoSchema(tags=["tensorflow-v1"])
    http_method_names = [
        "get",
        "options",
    ]

    def get(self, request: "Request", format=None, **kwargs):
        """`Historic camera records - filters= object type - camera_location - start_date - end_date - agg=time"""

        SUPPORTED_AGGREGATION_METHODS = ["sum", "average", "max", "min"]

        # Set default aggregation METHOD as Sum
        aggregation_method_str = request.query_params.get("aggregation_method", "sum").lower()

        if aggregation_method_str not in SUPPORTED_AGGREGATION_METHODS:
            return JsonResponse(
                data={
                    "error": f"Aggregation method {aggregation_method_str} not supported. Supported methods are {SUPPORTED_AGGREGATION_METHODS}"
                },
                status=400,
            )

        # Set the initial query set to be all camera records
        queryset = TF1Records.objects.all()

        # Get Start and End Date
        date_after = request.query_params.get("date_after", None)
        date_before = request.query_params.get("date_before", None)

        # Convert start and end dates to datetime objects - add date range filter
        if date_after is not None:
            date_after = datetime.strptime(date_after, "%d-%m-%Y")
            date_after = date_after.replace(tzinfo=timezone.utc)
            queryset = queryset.filter(timestamp__gte=date_after)

        if date_before is not None:
            date_before = datetime.strptime(date_before, "%d-%m-%Y")
            date_before = date_before.replace(tzinfo=timezone.utc)
            queryset = queryset.filter(timestamp__lte=date_before)

        # Get Object Types
        all_object_types = [
            "cars",
            "buses",
            "trucks",
            "motorcycles",
            "persons",
            "bicycles",
        ]
        object_types = request.query_params.getlist("object", all_object_types)

        # Camera Locations - Filter and
        cameras_qs = get_cameras_that_have_records()
        camera_ids = request.query_params.getlist("camera_id", None)

        if len(camera_ids):
            cameras_qs = cameras_qs.filter(id__in=camera_ids)

        # Set default DATE aggregation as day - daily values
        ## What are the other options?
        ## consider renaming to aggregation_period
        aggregation_date = request.query_params.get("aggregation", "day")
        aggregation_date = aggregation_date.lower()

        match aggregation_method_str:
            case "sum":
                aggregation_method = sum
            case "average":
                aggregation_method = mean
            case "min":
                aggregation_method = min
            case "max":
                aggregation_method = max
            case _:
                raise ValueError(f"Aggregation method {aggregation_method_str} not supported")

        # records qs; limited on requested cameras
        queryset = queryset.filter(camera__in=Subquery(cameras_qs.values("id")))

        annotated_queryset = aggregate_records_qs(queryset, aggregation_date, aggregation_method_str)

        # Filter Queryset by object type - sum their values and structure the records
        records_list = [
            {
                "timestamp": record["dateAgg"],
                "value": aggregation_method([record[item + "Agg"] for item in object_types]),
            }
            for record in annotated_queryset
        ]

        data = {
            "aggregation": aggregation_date,
            "aggregation_method": aggregation_method_str,
            "date_after": date_after,
            "date_before": date_before,
            "object_types": object_types,
            "camera_locations": cameras_qs.values_list("id", flat=True),
            "records": sorted(list(records_list), key=lambda x: x["timestamp"]),
        }

        return JsonResponse(HistoricTF1RecordsSerializer(data).data, status=200)


class TF1RecordsViewSet(generics.ListAPIView):
    """
    ##  Records
    """

    schema = AutoSchema(tags=["tensorflow-v1"])
    http_method_names = [
        "get",
        "options",
    ]
    serializer_class = TF1RecordSerialzer
    # filter_backends = (DjangoFilterBackend,)
    filterset_class = TF1RecordFilter

    def get_queryset(self) -> QuerySet:
        prohibited_dateranges = RecordsFilter.get_exclusion_intervals(model_name="tf2")

        queryset = TF1Records.objects.all()

        for interval_entry in prohibited_dateranges:
            camera_id = interval_entry["camera_id"]
            exclusion_intervals = interval_entry["exclusion_intervals"]
            for exclusion_interval in exclusion_intervals:
                starting_datetime = exclusion_interval[0]
                ending_datetime = exclusion_interval[1]
                queryset = queryset.exclude(camera_id=camera_id, timestamp__range=(starting_datetime, ending_datetime))

        return queryset
