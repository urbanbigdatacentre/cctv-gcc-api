import csv
import gzip
import io
from enum import Enum
from itertools import groupby
from logging import getLogger
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Literal
from zipfile import ZipFile

from django.db.models import Q
from pydantic.error_wrappers import ValidationError

from cctv_records.models import (
    Cameras,
    TF2Records,
    YOLORecords,
)
from cctv_records.schemas import TF2ReportRecord, YOLOReportRecord

logger = getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import Aggregate


def zip_open(zip_file: Path | IO[bytes], file_name: str) -> io.TextIOWrapper:
    """Wrapper function for zipfiles."""
    with ZipFile(zip_file) as zipfh:
        logger.info(f"Trying to extract {file_name}.")
        return io.TextIOWrapper(zipfh.open(file_name), encoding="utf8")


def process_uploaded_report(
    file_handler: io.TextIOWrapper,
    overwrite: bool = False,
) -> dict:
    """Processes an uploaded report file and adds the data to the database.

    file_handler: A file handler to the report file.
    """

    reportType = Enum("report_type", ["TF1", "TF2", "YOLO"])
    logger.info(f"overwrite: {overwrite}")

    # if overwrite is true, it's upsert
    ignore_conflicts = not overwrite
    update_conflicts = overwrite

    def discover_report_type(file_handler) -> reportType:
        dialect = csv.Sniffer().sniff(file_handler.read(1024))
        file_handler.seek(0)
        spamreader = csv.DictReader(file_handler, dialect=dialect)
        try:
            dict_from_csv = dict(next(spamreader))
            file_handler.seek(0)
        except StopIteration:
            raise ValueError("No data rows found in report file")

        try:
            model_name = dict_from_csv["model_name"].lower().strip()
        except KeyError:
            raise ValueError("Model name column is not present in the report file")

        match model_name:
            case "yolo":
                logger.info("is_yolo")
                return reportType.YOLO
            case "tf2":
                logger.info("is_tf2")
                return reportType.TF2
            case _:
                raise ValueError(f"Report model_name {model_name} is not supported")

    report_type = discover_report_type(file_handler)
    csv_reader = csv.DictReader(file_handler)
    match report_type:
        case reportType.TF2:
            csv_line_parser_model = TF2ReportRecord
            db_model = TF2Records
            update_fields = [
                "cars",
                "persons",
                "bicycles",
                "trucks",
                "motorcycles",
                "buses",
                "camera_ok",
            ]
        case reportType.YOLO:
            csv_line_parser_model = YOLOReportRecord
            db_model = YOLORecords
            update_fields = [
                "cars",
                "pedestrians",
                "cyclists",
                "motorcycles",
                "buses",
                "lorries",
                "vans",
                "taxis",
                "camera_ok",
            ]
        case _:
            raise ValueError(f"Report type {report_type} is not supported")

    parsed_rows = []
    for row in csv_reader:
        try:
            row = {k: None if v == "None" else v for k, v in row.items()}
            parsed_row = csv_line_parser_model(**row)  # type: ignore
            parsed_rows.append(parsed_row)
        except ValidationError as e:
            errors, model = e.args
            logger.error("Error parsing report file and trying to load it to model %s", model)
            raise e
    len_parsed_rows = len(parsed_rows)
    logger.info("prossesing report: %s rows", len_parsed_rows)

    # sorts by the group_name found in the filename
    parsed_rows.sort(key=lambda e: e.camera_id)
    for camera_id, group_elem_iteretor in groupby(parsed_rows, lambda e: e.camera_id):
        camera_records = list(map(lambda e: e.to_db_record(camera_id=camera_id), group_elem_iteretor))
        db_model.objects.bulk_create(
            camera_records,
            batch_size=1000,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields if overwrite else None,
            unique_fields=["timestamp", "camera_id"],  # type: ignore
        )
    logger.info("prossesing report: %s rows", len_parsed_rows)
    return {
        "status": "ok",
        "message": "Report file was processed successfully",
        "have_unknown_cameras": Cameras.objects.filter(is_complete=False).exists(),
        "pks_of_unknown_cameras": list(Cameras.objects.filter(is_complete=False).values_list("pk", flat=True)),
    }


def handle_uploaded_report_file(
    f: Any,
    overwrite: bool = False,
):
    logger.info(f"handle_uploaded_report_file: {f}")
    content = f.read()
    first_chnk = content[:12]
    is_zip = first_chnk.hex().upper().startswith("504B0304")
    is_gz = first_chnk.hex().upper().startswith("1F8B")
    if is_zip:
        logger.info("is_zip")
        file_handler = zip_open(io.BytesIO(content), "report.csv")
    elif is_gz:
        logger.info("is_gz")
        file_handler = gzip.open(io.BytesIO(content), "rt")
    else:
        raise ValueError("File is not a zip or gzip file")

    return process_uploaded_report(file_handler, overwrite=overwrite)


aggregation_time_unitsType = Literal["week", "day", "year", "quarter", "hour", "month"]
aggregation_methodType = Literal["sum", "average", "max", "min"]


def get_cameras_that_have_records(
    are_complete: bool = True,
):
    """Get a qs with the cameras that have records. Optionally filter by completeness."""

    sub1 = YOLORecords.objects.order_by("camera_id").values("camera_id").distinct().values_list("camera_id")
    sub2 = TF2Records.objects.order_by("camera_id").values("camera_id").distinct().values_list("camera_id")

    qs = Cameras.objects.filter(Q(id__in=sub1) | Q(id__in=sub2))

    if are_complete:
        qs = qs.filter(is_complete=True)

    return qs
