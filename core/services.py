from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connection, transaction
from django.utils import timezone

from psqlextra.partitioning import (
    PostgresPartitioningManager,
    PostgresCurrentTimePartitioningStrategy,
    PostgresTimePartitionSize,
    PostgresRangePartitioningStrategy,
)
from psqlextra.partitioning.range_partition import PostgresRangePartition
from psqlextra.partitioning.config import PostgresPartitioningConfig


class PartitioningService:
    """
    Service to manage PostgreSQL table partitions using django-postgres-extra.
    """

    def __init__(self, model, partition_size="month", extra_future=12):
        """
        :param model: Django model subclassing PostgresPartitionedModel
        :param partition_size: "month" | "year" | "day"
        :param extra_future: how many future periods to create beyond max timestamp
        """
        self.model = model
        self.partition_size = partition_size
        self.extra_future = extra_future
        self.default_table = f"{model._meta.db_table}_default"

    def _get_partition_size(self):
        """Return PostgresTimePartitionSize based on config."""
        if self.partition_size == "year":
            return PostgresTimePartitionSize(years=1)
        elif self.partition_size == "day":
            return PostgresTimePartitionSize(days=1)
        return PostgresTimePartitionSize(months=1)  # default: monthly

    def _get_time_range(self):
        """Get min/max timestamps from default partition."""
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT MIN(created_at), MAX(created_at) FROM {self.default_table}"
            )
            min_ts, max_ts = cursor.fetchone()

        if not max_ts:
            return None, None

        start = (min_ts or timezone.now()).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = (max_ts + relativedelta(**{f"{self.partition_size}s": self.extra_future})).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return start, end

    def sync_partitions(self):
        """Ensure partitions exist up to max timestamp + buffer."""
        start, end = self._get_time_range()
        if not end:
            return "✅ No data in default partition."

        # Estimate number of partitions to create
        delta = relativedelta(end, start)
        if self.partition_size == "year":
            count = delta.years + self.extra_future
        elif self.partition_size == "day":
            count = (end - start).days + self.extra_future
        else:  # month
            count = delta.years * 12 + delta.months + self.extra_future

        config = PostgresPartitioningConfig(
            model=self.model,
            strategy=PostgresCurrentTimePartitioningStrategy(
                size=self._get_partition_size(),
                count=count,
                max_age=None,
                name_format=None
            ),
        )

        manager = PostgresPartitioningManager([config])
        manager.sync()

        return f"✅ Synced partitions for {self.model.__name__} ({self.partition_size})."

    def move_default_data(self):
        """Move rows from default partition → correct partitions."""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.default_table}")
            rows = cursor.fetchall()

        if not rows:
            return "✅ No rows in default partition."

        # Map rows into model instances
        objs = [self.model(**dict(zip([f.name for f in self.model._meta.fields], row))) for row in rows]

        with transaction.atomic():
            self.model.objects.bulk_create(objs, ignore_conflicts=True)
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.default_table}")

        return f"✅ Moved {len(objs)} rows into partitions."
    
    def _generate_boundaries(self, start_date: datetime, end_date: datetime):
        """Generate boundaries for partitions between start_date and end_date."""
        boundaries = []

        if self.partition_size == "year":
            current = start_date.replace(month=1, day=1)
            while current <= end_date:
                boundaries.append(current)
                current = current + relativedelta(years=1)

        elif self.partition_size == "month":
            current = start_date.replace(day=1)
            while current <= end_date:
                boundaries.append(current)
                current = current + relativedelta(months=1)

        elif self.partition_size == "day":
            current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            while current <= end_date:
                boundaries.append(current)
                current = current + relativedelta(days=1)

        return boundaries
    
    def ensure_partitions_between(self, partition_by, start_date: datetime, end_date: datetime):
        """
        Ensure partitions exist between start_date and end_date.
        Creates them if missing, keeps existing ones.

        :param start_date: datetime (aligned to start of period ideally)
        :param end_date: datetime (inclusive range)
        :return: str status message
        """
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        # Count how many partitions are required
        delta = relativedelta(end_date, start_date)
        if self.partition_size == "year":
            count = delta.years + 1
        elif self.partition_size == "day":
            count = (end_date - start_date).days + 1
        else:  # month
            count = delta.years * 12 + delta.months + 1

        boundaries = self._generate_boundaries(start_date, end_date)

        # Define config
        config = PostgresPartitioningConfig(
            model=self.model,
            strategy=PostgresRangePartitioningStrategy(
                key=partition_by,  # your partition key
                boundaries=boundaries
            ),
        )

        # Sync partitions
        manager = PostgresPartitioningManager([config])
        manager.plan().apply()

        return (
            f"✅ Ensured partitions for {self.model.__name__} "
            f"from {start_date.date()} to {end_date.date()} ({self.partition_size}, {count} partitions)."
        )

    def ensure_and_repair(self):
        """High-level operation: sync partitions & repair default."""
        sync_msg = self.sync_partitions()
        move_msg = self.move_default_data()
        return f"{sync_msg}\n{move_msg}"
