Perfect ✅ — I’ll prepare a **developer-friendly documentation** for using **`django-postgres-extra`**, structured topic-wise and step-by-step, so your teammates can quickly understand and apply it in their Django projects.

Here’s the first version of the doc 👇

---

# 📘 Django Postgres Extra (psqlextra) — Developer Documentation

[`django-postgres-extra`](https://github.com/SectorLabs/django-postgres-extra) is a Django extension library that unlocks **PostgreSQL-specific features** not available in vanilla Django ORM.

This doc is a **step-by-step guide** covering installation, configuration, and usage of its major features (like partitions, constraints, indexes, and utilities).

---

## 🔹 1. Installation

```bash
pip install django-postgres-extra
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "psqlextra",
]
```

---

## 🔹 2. Partitioning Support

Partitioning allows large tables to be **split into smaller child tables** for performance & scalability.

### 2.1 Define a Partitioned Model

```python
from psqlextra.models import PostgresPartitionedModel

class Order(PostgresPartitionedModel):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class PartitioningMeta:
        method = "RANGE"
        key = ["created_at"]
```

* `method`: `RANGE` | `LIST` | `HASH`
* `key`: column(s) used for partitioning

### 2.2 Create Partitions

Partitions must be defined in **migrations**:

```python
from psqlextra.partitioning import RangePartitioningConfig
from datetime import date

partitioning = [
    RangePartitioningConfig(
        model=Order,
        key="created_at",
        boundaries=[
            date(2024, 1, 1),
            date(2024, 2, 1),
            date(2024, 3, 1),
        ],
    )
]
```

Run migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create:

* `order` (parent)
* `order_2024_01`, `order_2024_02`, etc. (child partitions)

### 2.3 Query Partitions Programmatically

```python
from psqlextra.manager import PostgresPartitioningManager

partitions = PostgresPartitioningManager().partitions(Order)
for p in partitions:
    print(p.name, p.range_from, p.range_to)
```

---

## 🔹 3. Constraints

Postgres Extra simplifies **unique constraints** across partitions.

```python
from psqlextra.models import PostgresPartitionedModel

class UserEmail(PostgresPartitionedModel):
    email = models.EmailField(unique=True)  # works across partitions!
    created_at = models.DateField()

    class PartitioningMeta:
        method = "RANGE"
        key = ["created_at"]
```

Without `psqlextra`, PostgreSQL doesn’t support global unique constraints across partitions. This library makes it possible.

---

## 🔹 4. Index Management

You can define **indexes on partitions** just like normal models:

```python
class Order(PostgresPartitionedModel):
    created_at = models.DateField()
    status = models.CharField(max_length=20)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
        ]
```

The index will be applied to **all partitions**.

---

## 🔹 5. Advanced Utilities

### 5.1 Bulk Insert / Upsert

`psqlextra` extends the ORM with **Postgres-only queries**.

```python
from psqlextra.query import ConflictAction

Order.objects.on_conflict(
    ["id"],
    ConflictAction.UPDATE,
    values={"amount": 100.0},
).insert(id=1, created_at="2024-01-01")
```

This performs an **UPSERT** (insert or update) with minimal code.

---

### 5.2 CI-Friendly Migrations

When working in CI/CD, you can check partitioning setup:

```bash
python manage.py check
```

This validates migrations for partitioned models.

---

### 5.3 Querying Partition Metadata

Example: Get raw partition table names and constraints:

```python
from django.db import connection

def get_partitions(table_name: str):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                inhrelid::regclass::text AS partition_name
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            WHERE parent.relname = %s;
        """, [table_name])
        return [row[0] for row in cursor.fetchall()]
```

---

## 🔹 6. Best Practices

* ✅ Define **PartitioningMeta** in models where partitions are required.
* ✅ Always create **partitions via migrations** to ensure consistency.
* ✅ Use `PostgresPartitioningManager` instead of raw SQL when possible.
* ✅ Use `on_conflict` for safe bulk inserts and upserts.
* ❌ Don’t mix partitioned and non-partitioned migrations manually.
* ❌ Avoid renaming partitions directly in the DB; always use migrations.

---

## 🔹 7. When to Use This Library?

Use `django-postgres-extra` if your project requires:

* ✅ PostgreSQL **partitioned tables**
* ✅ **Global unique constraints** across partitions
* ✅ **Efficient bulk inserts/upserts**
* ✅ **Advanced Postgres features** not available in vanilla Django ORM

---

## 🔹 8. References

* 📖 [Official Repo](https://github.com/SectorLabs/django-postgres-extra)
* 🐘 [PostgreSQL Partitioning Docs](https://www.postgresql.org/docs/current/ddl-partitioning.html)

---

👉 This documentation is designed so any new developer can onboard quickly.

Would you like me to also create a **ready-to-use template project structure** (with `models/`, `services/partition_service.py`, and example migrations) so your team can just clone and start using `django-postgres-extra`?
