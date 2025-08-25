# core/models.py
from psqlextra.models import PostgresPartitionedModel
from psqlextra.partitioning import PostgresTimePartitioningStrategy, PostgresTimePartitionSize
from psqlextra.types import PostgresPartitioningMethod


class TimePartitionedModel(PostgresPartitionedModel):
    """Generic base model for monthly partitioning by created_at."""

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["created_at"]
        # Partition per month
        range_interval = "1 month"

    class Meta:
        abstract = True
