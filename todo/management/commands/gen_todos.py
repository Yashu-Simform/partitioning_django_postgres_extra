from django.core.management.base import BaseCommand
import random
from datetime import datetime
from todo.models import TodoNonExisting


class Command(BaseCommand):
    help = "Generate dummy Todo records (fixed count: 150000)"

    def handle(self, *args, **options):
        num_records = 400000  # fixed count

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

        todos = []
        for i in range(num_records):
            title = random.choice(titles)
            description = random.choice(descriptions)

            # Random month Jan–Aug
            month = random.randint(1, 7)
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            created_at = datetime(2025, month, day, hour, minute)

            todos.append(
                TodoNonExisting(
                    title=f"{title} #{i+1}",
                    description=description,
                    is_completed=random.choice([True, False]),
                    created_at=created_at,
                )
            )

            if len(todos) >= 5000:
                TodoNonExisting.objects.bulk_create(todos, batch_size=5000)
                self.stdout.write(self.style.SUCCESS(f"Inserted {i+1} records..."))
                todos = []

        if todos:
            TodoNonExisting.objects.bulk_create(todos, batch_size=5000)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully inserted {num_records} records.")
        )