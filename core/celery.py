from celery import shared_task
from todo.models import Todo
from services import PartitioningService

@shared_task
def repair_todo_partitions():
    service = PartitioningService(Todo, partition_size="month", extra_future=12)
    result = service.ensure_and_repair()
    return result
