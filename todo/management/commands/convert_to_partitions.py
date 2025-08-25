import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction, connection

from psqlextra.partitioning import PostgresPartitioningManager, PostgresCurrentTimePartitioningStrategy, PostgresTimePartitionSize
from psqlextra.partitioning.config import PostgresPartitioningConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Convert existing Todo table into a partitioned table using django-postgres-extra."

    def handle(self, *args, **options):
        app_name = "todo"
        model_name = "todo"
        Todo = apps.get_model("todo", "Todo")

        # Step 1: Register Todo as partitioned model (month-wise)
        manager = PostgresPartitioningManager([
            PostgresPartitioningConfig(
                model=Todo,
                strategy=PostgresCurrentTimePartitioningStrategy(
                    size=PostgresTimePartitionSize(months=1),
                    count=12,  # create 12 partitions ahead
                ),
            )
        ])

        db_table_name = f'{app_name}_{model_name}'

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT to_regclass('{db_table_name}_old');")
            exists = cursor.fetchone()[0]

        if not exists:
            logger.info("Renaming existing todo table -> todo_old...")
            with connection.cursor() as cursor:
                cursor.execute(f"ALTER TABLE todo RENAME TO {db_table_name}_old;")

        logger.info("Running sync to create base partitioned table...")
        manager.sync(create=True, delete=False)

        # Step 2: Figure out historical data range from old table
        with connection.cursor() as cursor:
            cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM {db_table_name}_old;")
            min_date, max_date = cursor.fetchone()

        if not min_date or not max_date:
            logger.warning("No data found in {db_table_name}_old.")
            return

        logger.info(f"Existing data: {min_date} → {max_date}")

        # Step 3: Create required partitions covering this historical range
        start = datetime(min_date.year, min_date.month, 1)
        end = datetime(max_date.year, max_date.month, 1)

        current = start
        while current <= end:
            logger.info(f"Ensuring partition for {current.strftime('%Y-%m')}")
            manager.ensure_partitions(Todo, current, current + relativedelta(months=1))
            current += relativedelta(months=1)

        # Step 4: Move old data into new partitioned table
        with transaction.atomic():
            logger.info("Moving rows into partitioned table...")
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO {db_table_name} (id, title, description, is_completed, created_at)
                    SELECT id, title, description, is_completed, created_at
                    FROM {db_table_name}_old;
                """)

        logger.info("✅ Migration complete. Data is now in partitioned table.")
        logger.info("You can validate and DROP TABLE todo_old manually after verification.")
