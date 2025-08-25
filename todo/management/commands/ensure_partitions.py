from django.core.management.base import BaseCommand
from datetime import datetime
from todo.models import Todo, TodoNonExisting
from core.services import PartitioningService


class Command(BaseCommand):
    help = "Ensure partitions exist for a given date range."

    def add_arguments(self, parser):
        parser.add_argument(
            "--start",
            type=str,
            required=True,
            help="Start date in YYYY-MM-DD format"
        )
        parser.add_argument(
            "--end",
            type=str,
            required=True,
            help="End date in YYYY-MM-DD format"
        )
        parser.add_argument(
            "--size",
            type=str,
            choices=["day", "month", "year"],
            default="month",
            help="Partition size (default: month)"
        )

    def handle(self, *args, **options):
        start_date = datetime.strptime(options["start"], "%Y-%m-%d")
        end_date = datetime.strptime(options["end"], "%Y-%m-%d")
        size = options["size"]

        service = PartitioningService(TodoNonExisting, partition_size=size)
        result = service.ensure_partitions_between('created_at', start_date, end_date)

        self.stdout.write(self.style.SUCCESS(result))
