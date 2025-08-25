from django.core.management.base import BaseCommand
from django.db import connection
from datetime import datetime
from todo.models import TodoNonExisting


class Command(BaseCommand):
    help = "Run a sample query and print executed SQL"

    def handle(self, *args, **options):
        # todo = TodoNonExisting.objects.create(
        #     title="MARCH-task-1",
        #     description="This is a sample todo item in 2024-MARCH.",
        #     is_completed=False,
        #     created_at=datetime(2024, 3, 5, 12, 0, 0)
        # )
        todo1 = TodoNonExisting.objects.filter(title__endswith="#153")
        # todo1 = TodoNonExisting.objects.all()
        # todo2 = TodoNonExisting.objects.first()
        # print('Total records fetched: ', len(todo1))
        # print(f"Result: {todo1}")
        # print(f"First Todo: {todo2}")

        print(len(todo1))

        # Get last executed query details
        last_query = connection.queries[-1]
        sql = last_query.get('sql', '')
        exec_time = last_query.get('time', '0')

        self.stdout.write(self.style.WARNING(f"Executed SQL: {sql}"))
        self.stdout.write(self.style.WARNING(f"Execution Time: {exec_time} seconds"))
