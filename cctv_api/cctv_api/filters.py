from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms import ModelMultipleChoiceField
from django_filters import rest_framework as filters
from django_filters.widgets import DateRangeWidget
from functools import lru_cache

from cctv_records.models import Cameras, TF1Records, TF2Records, YOLORecords


class AAAA(ModelMultipleChoiceField):
    @lru_cache
    def label_from_instance(self, obj) -> str:
        # cam = Cameras.objects.get(pk=obj)
        return f"Camera-{obj.pk}: ({obj.label or 'No Label'})"
        return obj


class CommeonRecordFilter(filters.FilterSet):
    camera_ok = filters.MultipleChoiceFilter(
        method="camera_ok_filter",
        field_name="camera_ok",
        label="Working Camera",
        distinct=True,
        choices=(
            ("unknown", "Not-Known"),
            ("true", "Active"),
            ("false", "Deactivated"),
        ),
    )
    date = filters.DateFromToRangeFilter(
        widget=DateRangeWidget(attrs={"type": "date"}),
        # input_formats=["%Y%m%d", "%d-%m-%Y", "%d/%m/%Y"],
        method="date_filter",
        label="Start/End Date",
    )

    def date_filter(
        self,
        queryset: QuerySet,
        name,
        date_range: slice,
        *args,
        **kwargs,
    ):
        """Method to filter by date"""
        start_date = date_range.start
        end_date = date_range.stop
        if start_date is None and end_date is None:
            return queryset

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        return queryset

    def camera_ok_filter(self, queryset: QuerySet, name, *args, **kwargs):
        search_args: list[str] = sorted(args[0])
        if not len(search_args):
            return queryset

        q = Q()
        if "unknown" in args[0]:
            q |= Q(camera_ok__isnull=True)
        if "true" in args[0]:
            q |= Q(camera_ok=True)
        if "false" in args[0]:
            q |= Q(camera_ok=False)

        return queryset.filter(q)


class TF1RecordFilter(CommeonRecordFilter):
    camera_id = filters.ModelMultipleChoiceFilter(
        # field_name='camera__id',
        label="Camera ID",
        # method="camera_id_filter",
        field_name="camera_id",
        to_field_name="camera_id",
        queryset=TF1Records.objects.values("camera_id"),
    )
    camera_id.field_class = AAAA  # type: ignore

    class Meta:
        models = TF1Records

    # def camera_id_filter(self, queryset: QuerySet, name, *args, **kwargs):
    #     return queryset


class TF2RecordsFilter(CommeonRecordFilter):
    class Meta:
        models = TF2Records

    camera_id = filters.ModelMultipleChoiceFilter(
        label="Camera ID",
        field_name="camera_id",
        to_field_name="id",
        distinct=True,
        queryset=Cameras.objects.all(),
    )
    camera_id.field_class = AAAA  # type: ignore


class YOLORecordsFilter(CommeonRecordFilter):
    class Meta:
        models = YOLORecords

    camera_id = filters.ModelMultipleChoiceFilter(
        label="Camera ID",
        field_name="camera_id",
        to_field_name="id",
        queryset=Cameras.objects.all(),
    )
    camera_id.field_class = AAAA  # type: ignore


__all__ = ["TF1RecordFilter", "TF2RecordsFilter", "YOLORecordsFilter"]
