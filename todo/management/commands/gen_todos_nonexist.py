from django.core.management.base import BaseCommand
import random
from datetime import datetime, timedelta
from todo.models import TodoNonExisting


class Command(BaseCommand):
    help = "Generate dummy Todo records (fixed count: 150000 within Aug 2025 - Jul 2026)"

    def handle(self, *args, **options):
        num_records = 150000  # fixed count

        titles = [
            "Buy groceries", "Finish project report", "Plan vacation",
            "Workout session", "Pay electricity bill", "Meeting with client",
            "Doctor appointment", "Car service", "Birthday reminder", "Study session"
        ]

        descriptions = [
            "This is an important task.",
            "Need to finish this before the deadline.",
            "Optional, but would be good to complete.",
            "Follow up required.",
            "Waiting for confirmation from others."
        ]

        # Define start and end datetime range
        start_date = datetime(2025, 8, 1)   # Aug 1, 2025
        end_date = datetime(2026, 7, 31, 23, 59, 59)  # Jul 31, 2026 end of day
        delta_seconds = int((end_date - start_date).total_seconds())

        todos = []
        for i in range(num_records):
            title = random.choice(titles)
            description = random.choice(descriptions)

            # Pick random timestamp in the range
            random_seconds = random.randint(0, delta_seconds)
            created_at = start_date + timedelta(seconds=random_seconds)

            todos.append(
                TodoNonExisting(
                    title=f"{title} #{i+1}",
                    description=description,
                    is_completed=random.choice([True, False]),
                    created_at=created_at,
                )
            )

            # Insert in batches for efficiency
            if len(todos) >= 5000:
                TodoNonExisting.objects.bulk_create(todos, batch_size=5000)
                self.stdout.write(self.style.SUCCESS(f"Inserted {i+1} records..."))
                todos = []

        if todos:
            TodoNonExisting.objects.bulk_create(todos, batch_size=5000)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully inserted {num_records} records.")
        )
