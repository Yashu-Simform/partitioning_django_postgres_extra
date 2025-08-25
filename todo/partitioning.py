# myapp/partitioning.py
from dateutil.relativedelta import relativedelta

from psqlextra.partitioning import (
    PostgresPartitioningManager,
    PostgresCurrentTimePartitioningStrategy,
    PostgresTimePartitionSize,
)
from psqlextra.partitioning.config import PostgresPartitioningConfig

from .models import Todo, TodoNonExisting

manager = PostgresPartitioningManager([
    # PostgresPartitioningConfig(
    #     model=Todo,
    #     strategy=PostgresCurrentTimePartitioningStrategy(
    #         size=PostgresTimePartitionSize(months=1),   # one partition = 1 month
    #         count=12,                                   # create 12 future partitions
    #         max_age=relativedelta(months=6),            # drop older than 6 months
    #     ),
    # ),
    PostgresPartitioningConfig(
        model=TodoNonExisting,
        strategy=PostgresCurrentTimePartitioningStrategy(
            size=PostgresTimePartitionSize(months=1),   # one partition = 1 month
            count=12,                                   # create 12 future partitions
            max_age=relativedelta(months=6),            # drop older than 6 months
        ),
    ),
])
