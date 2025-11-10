from pathlib import Path
import datetime
from turtle import pen
import pyexcel
from django.core.management.base import BaseCommand
import pendulum

from cctv_records.models import RecordsFilter, Cameras
import time
import platform
from typing import ClassVar

MAX_WAIT_SECONDS = 5 * 60  # 5 minutes
UTC = pendulum.timezone("UTC")


def datetime_to_str(dt: datetime.datetime):
    """Convert datetime to ISO 8601 string with timezone info"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.isoformat()


def str_to_datetime(dt_str: str):
    """Convert ISO 8601 string to datetime with timezone info"""
    dt = pendulum.parse(dt_str)
    if not isinstance(dt, pendulum.DateTime):
        raise ValueError(
            f"Could not parse datetime string: {dt_str}; see example of valid strings at https://pendulum.eustace.io/docs/#rfc-3339 and after"
        )
    return dt


def _is_locked(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        f = open(path, "r+b")
    except PermissionError:
        return True
    try:
        if platform.system() == "Windows":
            import msvcrt

            # Try non-blocking lock on 1 byte
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        f.close()
        return False
    except OSError:
        f.close()
        return True


class Command(BaseCommand):
    help = "synchronise camera records from excel file. If the excel file is not found a new excel file with the current camera records will be created."

    _meta = {
        "required_columns": ["camera_id", "model", "from_datetime", "to_datetime", "delete_mark"],
        "records_created": 0,
        "records_updated": 0,
        "records_skipped": 0,
        "records_removed": 0,
    }
    excel_path: Path

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/record_filter.xlsx",
            help="Path to the Excel file (default: data/record_filter.xlsx)",
        )

    def handle(self, *args, **options):
        self.excel_path = Path(options["file"])

        # Create data directory if it doesn't exist
        self.excel_path.parent.mkdir(parents=True, exist_ok=True)

        if self.excel_path.exists():
            self.stdout.write(self.style.SUCCESS(f"Found Excel file at {self.excel_path}"))
            self._wait_for_unlock()
            self._sync_from_excel(self.excel_path)
            self._export_to_excel(self.excel_path)
        else:
            self.stdout.write(self.style.WARNING(f"Excel file not found at {self.excel_path}"))
            self._export_to_excel(self.excel_path)

    def _wait_for_unlock(self):
        elapsed = 0
        while _is_locked(self.excel_path):
            if elapsed == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"{self.excel_path} appears locked (maybe open in Excel). Waiting up to {MAX_WAIT_SECONDS}s..."
                    )
                )
            time.sleep(5)
            elapsed += 5
            if elapsed >= MAX_WAIT_SECONDS:
                self.stdout.write(
                    self.style.ERROR(f"{self.excel_path} is still locked after {MAX_WAIT_SECONDS}s. Aborting export.")
                )
                return

    def _create_missing_records(self, records):
        for record in records:
            delete_mark = str(record.get("delete_mark", "")).strip().lower()
            if delete_mark == "yes" or delete_mark == "true" or delete_mark == "1":
                continue  # skip creation of records marked for deletion

            camera_id = str(record.get("camera_id", "")).strip()
            model = str(record.get("model", "")).strip()
            from_datetime_str = str(record.get("from_datetime", "")).strip()
            to_datetime_str = str(record.get("to_datetime", "")).strip()

            if not camera_id or not model or not from_datetime_str or not to_datetime_str:
                self.stdout.write(self.style.WARNING(f"Skipping record with missing required fields: {record}"))
                self._meta["records_skipped"] += 1
                continue

            try:
                from_datetime = str_to_datetime(from_datetime_str)
                to_datetime = str_to_datetime(to_datetime_str)
            except ValueError as e:
                self.stdout.write(
                    self.style.WARNING(f"Skipping record with invalid datetime format: {record}. Error: {e}")
                )
                self._meta["records_skipped"] += 1
                continue

            existing = RecordsFilter.objects.filter(
                camera__camera_id=camera_id,
                model=model,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            ).first()

            if existing:
                self.stdout.write(self.style.NOTICE(f"Record already exists, skipping: {record}"))
                self._meta["records_skipped"] += 1
                continue

            # Create new record
            camera = Cameras.objects.filter(camera_id=camera_id).first()
            if not camera:
                self.stdout.write(
                    self.style.WARNING(f"Camera with ID {camera_id} does not exist. Skipping record: {record}")
                )
                self._meta["records_skipped"] += 1
                continue

            new_record = RecordsFilter(
                camera=camera,
                model=model,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            )
            new_record.save()
            self.stdout.write(self.style.SUCCESS(f"Created new record: {record}"))
            self._meta["records_created"] += 1

    def _delete_marked_records(self, records):
        for record in records:
            delete_mark = str(record.get("delete_mark", "")).strip().lower()
            if delete_mark != "yes" and delete_mark != "true" and delete_mark != "1":
                continue  # skip records not marked for deletion

            camera_id = str(record.get("camera_id", "")).strip()
            model = str(record.get("model", "")).strip()
            from_datetime_str = str(record.get("from_datetime", "")).strip()
            to_datetime_str = str(record.get("to_datetime", "")).strip()

            if not camera_id or not model or not from_datetime_str or not to_datetime_str:
                self.stdout.write(
                    self.style.WARNING(f"Skipping deletion for record with missing required fields: {record}")
                )
                continue

            try:
                from_datetime = str_to_datetime(from_datetime_str)
                to_datetime = str_to_datetime(to_datetime_str)
            except ValueError as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping deletion for record with invalid datetime format: {record}. Error: {e}"
                    )
                )
                continue

            existing = RecordsFilter.objects.filter(
                camera__camera_id=camera_id,
                model=model,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            ).first()

            if existing:
                existing.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted record: {record}"))
                self._meta["records_removed"] += 1
            else:
                self.stdout.write(self.style.NOTICE(f"No matching record found to delete for: {record}"))

    def _sync_from_excel(self, excel_path: Path):
        """Read records filter from Excel file and sync the database"""
        sheet = pyexcel.get_sheet(file_name=str(excel_path), name_columns_by_row=0)
        records = list(sheet.to_records())
        if not records:
            self.stdout.write(self.style.WARNING("Excel file is empty"))
            return
        headers = list(records[0].keys()) if records else []
        missing_columns = [col for col in self._meta["required_columns"] if col not in headers]
        if missing_columns:
            self.stdout.write(self.style.ERROR(f"Missing required columns: {missing_columns}"))
            return

        self._create_missing_records(records)
        # self._update_existing_records(records)
        self._delete_marked_records(records)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSync complete: {self._meta['records_created']} created, {self._meta['records_updated']} updated, {self._meta['records_skipped']} skipped"
            )
        )

    def _export_to_excel(self, excel_path: Path):
        """Export current camera records to Excel file"""
        records = RecordsFilter.objects.all()

        data = []
        headers = self._meta["required_columns"]

        for record in records:
            data.append(
                [
                    record.camera.camera_id,
                    record.model,
                    datetime_to_str(record.from_datetime),
                    datetime_to_str(record.to_datetime),
                    "",  # delete_mark; always empty on export
                ]
            )

        # Create sheet with headers and data
        sheet = pyexcel.Sheet([headers] + data, name="record_filter")

        # Save to Excel file
        sheet.save_as(str(self.excel_path))
        self.stdout.write(self.style.SUCCESS(f"Exported {len(data)} camera records to {self.excel_path}"))
