# Rule: CSV Ingestion Layer

When adding CSV ingestion for a new entity, follow these patterns exactly.

---

## 1. Plain Function Pattern

All ingestion is done via plain async functions in `scripts/ingest.py`:

```python
async def ingest_<entity>(db: AsyncSession, fail_fast: bool = False) -> dict[str, Any]:
    """Ingest <entity> from CSV using native PostgreSQL upsert."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "<entity>.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    items: list[<Entity>Create] = []
    errors: list[dict] = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # validate headers, parse rows, collect per-row errors
        ...

    # Deduplicate within CSV by unique key (keep last occurrence)
    ...

    # Native PostgreSQL upsert in batches
    ...

    return {"created": n, "updated": m, "errors": len(errors), "error_details": errors}
```

No `BaseHandler`, `HandlerRegistry`, or `ValidationError` class. Register nothing — call functions directly from `main()`.

CSV file must be at `backend/data/<entity>.csv`.

---

## 2. Validation Rules (per row)

| Check | Implementation |
|-------|----------------|
| **Required field present** | `if not row["field"].strip(): raise ValueError(...)` |
| **Type conversion** | `int(row["count"])` with try/except → `ValueError` |
| **Range/constraint** | `if value < 0: raise ValueError(...)` |
| **Date parsing** | Try multiple formats, raise `ValueError` on failure |
| **Custom business rules** | Add as needed (e.g., unique combinations) |

Wrap row parsing in try/except, append `{"row": row_num, "field": "...", "error": str(e)}` to errors list. If `fail_fast`, break on first error.

---

## 3. Bulk Upsert Pattern (native PostgreSQL)

```python
# 1. Deduplicate within CSV by unique key (keep last occurrence)
seen: dict[unique_key, Item] = {}
for item in items:
    seen[unique_key] = item
items = list(seen.values())

# 2. Native PostgreSQL upsert in batches
batch_size = 500
for i in range(0, len(items), batch_size):
    chunk = items[i:i + batch_size]
    stmt = insert(Entity).values([item.model_dump() for item in chunk])
    stmt = stmt.on_conflict_do_update(
        index_elements=[unique_key_columns],
        set_={
            "col1": stmt.excluded.col1,
            "col2": stmt.excluded.col2,
        }
    )
    await db.execute(stmt)
```

- Use `on_conflict_do_update()` with `index_elements` when you want to update existing rows on conflict
- Use `on_conflict_do_nothing()` (no index elements) when any unique constraint conflict should be skipped
- Import: `from sqlalchemy.dialects.postgresql import insert`
- Always `await db.flush()` after all batches; `main()` handles `await db.commit()`

---

## 4. Username Generation (members only)

For members, generate unique usernames in Python:
1. Collect all base usernames from CSV rows
2. Pre-fetch existing usernames matching `base%` in ONE query with `or_(*[Member.username.like(p) for p in patterns])`
3. Compute next available suffix per base, tracking a local counter
4. Insert new members with `on_conflict_do_nothing()` as a safety net

---

## 5. Output Format

Return dict (always includes `error_details`):

```python
{"created": n, "updated": m, "errors": k, "error_details": [...]}
```

The ingestion run prints:
```
Running handler: <entity>
  Created: 5, Updated: 2, Errors: 3
  Validation Errors (3):
    Row 4, Field 'date': Invalid date format: '32/01/2025'. Use DD/MM/YYYY or YYYY-MM-DD
    Row 7, Field 'count': Must be an integer
```

---

## 6. Key Principles

1. **Per-row validation, partial success**: Invalid rows are reported as errors but valid rows are still processed. NOT all-or-nothing.
2. **CSV dedup**: Deduplicate within the CSV file by unique key before upserting (keep last occurrence).
3. **Native PostgreSQL upsert**: `insert().on_conflict_do_update()` / `on_conflict_do_nothing()` — eliminates race conditions and read-modify-write.
4. **Batched**: 500 rows per batch to avoid oversized statements.
5. **Single query fetches**: Use `IN` clause or `tuple_.in_()` for bulk lookups of existing rows.
6. **`flush()` + `commit()`**: Single `flush()` after all batches; `main()` calls `commit()`.
7. **Error details always included**: `error_details: []` in all return dicts.
8. **No registry**: Plain functions called directly from `main()`, no `Handler`/`Registry` classes.
