import logging
from datetime import datetime
from typing import Annotated, Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify

logger = logging.getLogger(f"cctv.{__name__}")


class LowerTextField(models.TextField):
    def get_prep_value(self, value: str) -> str:
        return str(value).lower()


class ModelChoices(models.TextChoices):
    TF1 = ("tf1", "TF1")
    TF2 = ("tf2", "TF2")
    YOLO = ("yolo", "YOLO")


class RecordsFilter(models.Model):
    camera = models.ForeignKey("Cameras", on_delete=models.CASCADE)
    model = models.CharField(
        choices=ModelChoices.choices,
        default=ModelChoices.YOLO,
        max_length=10,
    )
    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()

    def clean(self) -> None:
        if self.to_datetime < self.from_datetime:
            raise ValidationError({"to_datetime": "to_datetime must be greater than from_datetime."})
        if self.from_datetime > self.to_datetime:
            raise ValidationError({"from_datetime": "from_datetime must less than to_datetime."})
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @classmethod
    def get_exclusion_intervals(cls, model_name: str | None = None, camera: "Cameras | str | None" = None) -> list[Any]:
        "Returns a list of datetime intervals where the records should be hidden"

        from cctv_records.helpers import merge_intervals

        exclusion_intervals = cls.objects.all()
        if model_name:
            assert model_name in ModelChoices.values
            exclusion_intervals = exclusion_intervals.filter(model=model_name)
        if camera:
            if isinstance(camera, str):
                camera = Cameras.objects.get(camera_id=camera)
            exclusion_intervals = exclusion_intervals.filter(camera=camera)

        # SQLite-compatible grouping and aggregation
        exclusion_intervals_all = []
        cameras_models = exclusion_intervals.values_list("camera", "model").distinct()
        for camera_id, model in cameras_models:
            intervals = exclusion_intervals.filter(camera=camera_id, model=model).values_list(
                "from_datetime", "to_datetime"
            )
            exclusion_intervals_all.append(
                {
                    "camera_id": camera_id,
                    "model": model,
                    "exclusion_intervals": merge_intervals(list(intervals)),
                }
            )

        return exclusion_intervals_all


class Cameras(models.Model):
    """Camera Locations and Info"""

    camera_id = LowerTextField(
        unique=True,
        null=False,
        help_text="Camera reference code (don't publish). Lowercase only.",
    )
    label = models.TextField(help_text="Description/Label of Camera", null=False)
    longitude = models.FloatField(help_text="Camera Location longitude (EPSG:4326)", null=True)
    latitude = models.FloatField(help_text="Camera Location latitude (EPSG:4326)", null=True)
    is_complete = models.BooleanField(help_text="Is the camera data complete?", default=False, editable=True)

    class Meta:
        db_table = "camera_cameras"
        ordering = ["camera_id"]
        verbose_name_plural = "Cameras"

    def get_exclusion_intervals(self, model_name: str) -> list[Annotated[list[datetime], 2]]:
        """Returns a list of datetime intervals where the records should be hidden"""
        from cctv_records.helpers import merge_intervals

        datetime_intervals_qs = RecordsFilter.objects.filter(camera=self, model=model_name).values_list(
            "from_datetime", "to_datetime"
        )
        datetime_intervals = list(datetime_intervals_qs)
        merged_intervals = merge_intervals(datetime_intervals)

        return merged_intervals

    @staticmethod
    def create_camera(
        camera_id: str,
        longitude: float,
        latitude: float,
    ) -> "Cameras":
        camera = Cameras.objects.create(camera_id=camera_id, longitude=longitude, latitude=latitude)

        return camera

    def save(self, *args, **kwargs):
        self.camera_id = self.camera_id.lower().replace(" ", "")
        has_lat = self.latitude is not None
        has_long = self.longitude is not None
        has_label = self.label is not None
        if has_lat and has_long and has_label:
            self.is_complete = True

        return super().save(*args, **kwargs)

    def __str__(self):
        pk = self.pk
        camera_ref = self.camera_id

        return f"CCTVCamera({pk}-{camera_ref})"


class RecordCommonFields(models.Model):
    """Common Fields for all Record Models"""

    class IsCameraOkChoices(models.TextChoices):
        NONE = (None, "Unknown")
        TRUE = (True, "True")
        FALSE = (False, "False")

    class Meta:
        abstract = True

    camera = models.ForeignKey(
        "cctv_records.Cameras",
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_cameras",
        help_text="Camera Location",
        related_query_name="%(app_label)s_%(class)s_cameras",
    )
    timestamp = models.DateTimeField(help_text="Datetime of the capture.", null=False)
    camera_ok = models.BooleanField(
        null=True,
        choices=IsCameraOkChoices.choices,
        # default=None,
        help_text="A T/F/Null flag if the camera was operating normally the time of"
        " capture. null values mean it was unknown. ",
    )


class TF1Records(RecordCommonFields):
    """Main Table to hold tf1 records. Links with Cameras"""

    cars = models.IntegerField(help_text="Number of cars", default=None, null=True)
    persons = models.IntegerField(help_text="Number of persons.", default=None, null=True)
    bicycles = models.IntegerField(help_text="Number of bicycles.", default=None, null=True)
    trucks = models.IntegerField(help_text="Number of trucks.", default=None, null=True)
    motorcycles = models.IntegerField(help_text="Number of motorcycles.", default=None, null=True)
    buses = models.IntegerField(help_text="Number of buses.", default=None, null=True)

    model_name = models.TextField(default="tf1", editable=False)

    def __str__(self):
        return f"TF1Record: {self.pk}"

    class Meta:
        db_table = "tf1_records"
        ordering = ("-timestamp", "camera")
        constraints = (
            models.UniqueConstraint(
                fields=["timestamp", "camera"],
                name="tf1_unique_timestamp_camera",
            ),
        )
        verbose_name_plural = "TF1Records"


class TF2Records(RecordCommonFields):
    cars = models.IntegerField(help_text="Number of cars", default=None, null=True)
    persons = models.IntegerField(help_text="Number of persons.", default=None, null=True)
    bicycles = models.IntegerField(help_text="Number of bicycles.", default=None, null=True)
    trucks = models.IntegerField(help_text="Number of trucks.", default=None, null=True)
    motorcycles = models.IntegerField(help_text="Number of motorcycles.", default=None, null=True)
    buses = models.IntegerField(help_text="Number of busses.", default=None, null=True)

    model_name = models.TextField(help_text="Model Name", null=False, default="tf2", editable=False)

    def __str__(self):
        return f"TF2Record: {self.pk}"

    class Meta:
        db_table = "tf2_records"
        ordering = ("-timestamp", "camera")
        constraints = (
            models.UniqueConstraint(
                fields=["timestamp", "camera"],
                name="tf2_unique_timestamp_camera",
            ),
        )
        verbose_name_plural = "TF2Records"


class YOLORecords(RecordCommonFields):
    model_name = models.TextField(help_text="Model Name", default="yolo", editable=False)
    cars = models.IntegerField(help_text="Number of cars", default=None, null=True)
    pedestrians = models.IntegerField(help_text="Number of pedestrians", default=None, null=True)
    cyclists = models.IntegerField(help_text="Number of cyclists", default=None, null=True)
    motorcycles = models.IntegerField(help_text="Number of motorcycles", default=None, null=True)
    buses = models.IntegerField(help_text="Number of buses", default=None, null=True)
    lorries = models.IntegerField(help_text="Number of lorries", default=None, null=True)
    vans = models.IntegerField(help_text="Number of vans", default=None, null=True)
    taxis = models.IntegerField(help_text="Number of taxis", default=None, null=True)

    def __str__(self):
        return f"YOLORecord: {self.pk}"

    class Meta:
        db_table = "yolo_records"
        ordering = ("-timestamp", "camera")
        constraints = (
            models.UniqueConstraint(
                fields=["timestamp", "camera"],
                name="yolo_unique_timestamp_camera",
            ),
        )
        verbose_name_plural = "YOLORecords"


__all__ = [
    "Cameras",
    "TF1Records",
    "TF2Records",
    "YOLORecords",
]
