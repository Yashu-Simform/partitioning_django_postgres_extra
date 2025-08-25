from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from todo.models import TodoNonExisting, Todo


def get_partitioned_todos(months: int = 3, start_date: datetime | None = None):
    """
    Fetch todos for a range of months (default = last 3 months).
    - months: how many months of data to fetch
    - start_date: optional reference date (defaults to now)
    """
    if start_date is None:
        start_date = datetime(2026,3,1)

    # Ensure it's timezone-aware
    start_date = make_aware(start_date)

    # Calculate date window
    end_date = start_date
    start_range = start_date - relativedelta(months=months)

    return TodoNonExisting.objects.filter(
        created_at__gte=start_range, created_at__lt=end_date
    ).order_by("-created_at")
