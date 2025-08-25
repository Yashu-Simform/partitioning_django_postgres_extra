from django.db import models
from datetime import datetime

class Todo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now())  # useful for monthly partition later

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),  # helps with partitioning & queries
        ]

    def __str__(self):
        return self.title

from core.basemodels import TimePartitionedModel
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod
from django.db import models
from datetime import datetime

class TodoNonExisting(TimePartitionedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)  # Optional field for deadlines
    status = models.DateTimeField(blank=True, null=True)  # Optional field for deadlines
    # created_at = models.DateTimeField(auto_now_add=True) # Uncomment it when in production
    created_at = models.DateTimeField(default=datetime.now()) # For inserting the whole records manually

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["created_at"]
        # Partition per month
        range_interval = "1 month"

    class Meta:
        indexes = [
            models.Index(fields=["title"]),  # helps with partitioning & queries
        ]

    def __str__(self):
        return self.title
