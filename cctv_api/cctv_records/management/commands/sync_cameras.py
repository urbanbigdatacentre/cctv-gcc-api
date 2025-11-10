from pathlib import Path

import pyexcel
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.management.base import BaseCommand

from cctv_records.models import Cameras
import time
import platform


MAX_WAIT_SECONDS = 5 * 60  # 5 minutes


class Command(BaseCommand):
    help = "synchronise camera records from excel file. If the excel file is not found a new excel file with the current camera records will be created."

    _meta = {
        "required_columns": ["camera_id", "label", "longitude", "latitude"],
        "cameras_added": 0,
        "cameras_updated": 0,
        "cameras_skipped": 0,
        "cameras_removed": 0,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/cameras.xlsx",
            help="Path to the Excel file (default: data/cameras.xlsx)",
        )

    def handle(self, *args, **options):
        excel_path = Path(options["file"])

        # Create data directory if it doesn't exist
        excel_path.parent.mkdir(parents=True, exist_ok=True)

        if excel_path.exists():
            self.stdout.write(self.style.SUCCESS(f"Found Excel file at {excel_path}"))
            self._sync_from_excel(excel_path)
            self._export_to_excel(excel_path)
        else:
            self.stdout.write(self.style.WARNING(f"Excel file not found at {excel_path}"))
            self._export_to_excel(excel_path)

    def _sync_from_excel(self, excel_path: Path):
        """Read camera data from Excel and sync with database"""
        # Load Excel file as records (list of dictionaries)
        sheet = pyexcel.get_sheet(file_name=str(excel_path), name_columns_by_row=0)

        # Convert to records (list of dicts with headers as keys)
        records = list(sheet.to_records())

        if not records:
            self.stdout.write(self.style.WARNING("Excel file is empty"))
            return

        headers = list(records[0].keys()) if records else []
        missing_columns = [col for col in self._meta["required_columns"] if col not in headers]

        if missing_columns:
            self.stdout.write(self.style.ERROR(f"Missing required columns: {missing_columns}"))
            return

        self._create_missing_cameras(records)
        self._update_existing_cameras(records)
        # self._delete_nonexistent_cameras(records)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSync complete: {self._meta['cameras_added']} created, {self._meta['cameras_updated']} updated, {self._meta['cameras_skipped']} skipped"
            )
        )

    def _update_existing_cameras(self, records):
        """Update existing camera records based on Excel data"""
        updated_count = 0

        for record in records:
            camera_id = str(record.get("camera_id")).lower().strip().replace(" ", "")
            try:
                camera = Cameras.objects.get(camera_id=camera_id)
                camera.label = record.get("label")
                camera.longitude = record.get("longitude")
                camera.latitude = record.get("latitude")
                camera.full_clean()
                camera.save()
                updated_count += 1
            except Cameras.DoesNotExist:
                continue
            except DjangoValidationError as e:
                self.stdout.write(self.style.ERROR(f"Validation error for {camera_id}: {e}"))
        self._meta["cameras_updated"] = updated_count
        return

    def _delete_nonexistent_cameras(self, records):
        """Remove cameras not present in the Excel records"""
        existing_camera_ids = {
            str(record.get("camera_id")).lower().strip().replace(" ", "")
            for record in records
            if record.get("camera_id")
        }
        cameras_to_delete = Cameras.objects.exclude(camera_id__in=existing_camera_ids)

        deleted_count = cameras_to_delete.count()
        cameras_to_delete.delete()
        self._meta["cameras_removed"] = deleted_count

        self.stdout.write(self.style.SUCCESS(f"Removed {deleted_count} cameras not present in the Excel file"))

    def _create_missing_cameras(self, records):
        create_count = 0
        for record in records:
            camera_id = str(record.get("camera_id")).lower().strip().replace(" ", "")
            if not Cameras.objects.filter(camera_id=camera_id).exists():
                camera = Cameras(
                    camera_id=camera_id,
                    label=record.get("label"),
                    longitude=record.get("longitude"),
                    latitude=record.get("latitude"),
                )
                try:
                    camera.full_clean()
                    camera.save()
                    create_count += 1
                except DjangoValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Validation error for {camera_id}: {e}"))
                    self._meta["cameras_skipped"] += 1
            else:
                self._meta["cameras_skipped"] += 1

        self._meta["cameras_added"] = create_count

    def _export_to_excel(self, excel_path: Path):
        """Export current camera records to Excel file"""

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

        elapsed = 0
        while _is_locked(excel_path):
            if elapsed == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"{excel_path} appears locked (maybe open in Excel). Waiting up to {MAX_WAIT_SECONDS}s..."
                    )
                )
            time.sleep(5)
            elapsed += 5
            if elapsed >= MAX_WAIT_SECONDS:
                self.stdout.write(
                    self.style.ERROR(f"{excel_path} is still locked after {MAX_WAIT_SECONDS}s. Aborting export.")
                )
                return

        cameras = Cameras.objects.all()
        # Prepare data for export
        data = []
        headers = ["camera_id", "label", "longitude", "latitude"]

        for camera in cameras:
            try:
                data.append(
                    [
                        camera.camera_id,
                        camera.label,
                        camera.longitude,
                        camera.latitude,
                    ]
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping camera {camera.camera_id}: {e}"))

        # Create sheet with headers and data
        sheet = pyexcel.Sheet([headers] + data, name="Cameras")

        # Save to Excel file
        sheet.save_as(str(excel_path))

        self.stdout.write(self.style.SUCCESS(f"Exported {len(data)} camera records to {excel_path}"))
