from django.core.management.base import BaseCommand, CommandError
from cctv_records.utils import process_uploaded_report
import gzip

from pathlib import Path


class Command(BaseCommand):
    help = "Import records from a CSV file into a Django model."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help="Path to the CSV file")
        parser.add_argument(
            "--encoding",
            default="utf-8",
            help="File encoding (default: utf-8)",
        )

    def handle(self, *args, **options):
        csv_path: Path = Path(options["csv_file"])

        if csv_path.suffix.lower() not in {".gz"}:
            raise CommandError("Invalid file format. Please provide a .gz file.")

        with gzip.open(csv_path, "rt") as stream:
            process_uploaded_report(stream)

        self.stdout.write(self.style.SUCCESS("file imported successfully."))
