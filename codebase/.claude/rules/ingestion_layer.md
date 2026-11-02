# Rule: CSV Ingestion Layer

When adding CSV ingestion for a new entity, follow these patterns exactly.

---

## 1. Base Handler Pattern

All handlers extend `BaseHandler` in `scripts/ingest.py`:

```python
class EntityHandler(BaseHandler):
    REQUIRED_COLUMNS = ["col1", "col2", "col3"]  # Must match CSV headers exactly

    def get_csv_filename(self) -> str:
        return "entity.csv"

    def parse_row(self, row: dict[str, str], row_num: int) -> EntityCreate:
        # Validate & transform each field
        # Raise ValidationError(row_num, field, message) for any issue
        return EntityCreate(...)

    async def process_all(self, items: list[EntityCreate]) -> dict[str, int]:
        # Bulk upsert logic (fetch existing → split create/update → add_all + flush)
        return {"created": n, "updated": m, "errors": 0, "error_details": []}
```

---

## 2. Validation Rules (in `parse_row`)

| Check | Implementation |
|-------|----------------|
| **Required field present** | `if not row["field"].strip(): raise ValidationError(...)` |
| **Type conversion** | `int(row["count"])` with try/except → `ValidationError` |
| **Range/constraint** | `if value < 0: raise ValidationError(...)` |
| **Date parsing** | Try multiple formats, raise `ValidationError` on failure |
| **Custom business rules** | Add as needed (e.g., unique combinations) |

**ValidationError signature:**
```python
raise ValidationError(row_num: int, field: str, message: str)
```

---

## 3. Bulk Upsert Pattern (in `process_all`)

```python
async def process_all(self, items: list[EntityCreate]) -> dict[str, int]:
    if not items:
        return {"created": 0, "updated": 0, "errors": 0, "error_details": []}

    # 1. Fetch existing by unique key in ONE query
    keys = [item.unique_field for item in items]
    result = await self.db.execute(
        select(Entity).where(Entity.unique_field.in_(keys))
    )
    existing_map = {e.unique_field: e for e in result.scalars()}

    # 2. Split create vs update
    to_create, to_update = [], []
    for item in items:
        if item.unique_field in existing_map:
            to_update.append((existing_map[item.unique_field], item))
        else:
            to_create.append(item)

    # 3. Bulk insert
    if to_create:
        self.db.add_all([Entity(**item.model_dump()) for item in to_create])

    # 4. Bulk update (preserve immutable fields like username)
    for existing, item in to_update:
        for k, v in item.model_dump(exclude_unset=True, exclude={"immutable_field"}).items():
            setattr(existing, k, v)

    await self.db.flush()
    return {"created": len(to_create), "updated": len(to_update), "errors": 0, "error_details": []}
```

---

## 4. Register Handler

In `main()`:
```python
registry.register("entity", EntityHandler)
```

CSV file must be at `scripts/entity.csv`.

---

## 5. Output Format

The ingestion run prints:
```
Running handler: entity
  Created: 5, Updated: 2, Errors: 3
  Validation Errors (3):
    Row 4, Field 'date': Invalid date format: '32/01/2025'. Use DD/MM/YYYY or YYYY-MM-DD
    Row 7, Field 'count': Must be an integer
```

---

## 6. Key Principles

1. **All-or-nothing**: If ANY validation error → NO rows processed (returns `created: 0, updated: 0`)
2. **Single query fetches**: Use `IN` clause for bulk lookups
3. **`add_all()` + single `flush()`**: Efficient bulk operations
4. **Preserve immutable fields**: Exclude `username`, `id`, etc. from updates
5. **Error details always included**: `error_details: []` in all return dicts