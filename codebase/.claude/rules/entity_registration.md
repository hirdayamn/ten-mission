# Rule: Registering a New Service or Entity

When adding a new entity (e.g., `Product`, `Category`, `Supplier`), **do not generate code immediately**. First, interactively confirm these details:

### 1. Entity Specification
- **Name**: Singular (`Product`) and plural (`products`)
- **Purpose**: One-line description
- **Fields**: Column name, SQL type, constraints (PK, FK, unique, nullable, default, index)
- **Relationships**: Foreign keys to existing models

### 2. API Endpoints Needed
| Operation | Endpoint | Notes |
|-----------|----------|-------|
| List (paginated, searchable) | `GET /api/<plural>` | query: `q`, `page`, `page_size` |
| Get by ID | `GET /api/<plural>/{id}` | UUID |
| Create | `POST /api/<plural>` | |
| Update | `PATCH /api/<plural>/{id}` | partial |
| Delete | `DELETE /api/<plural>/{id}` | soft/hard |
| Custom | (specify) | e.g., bulk, filters |

### 3. Business Rules
- Validation (e.g., unique title, stock ≥ 0)
- Concurrency (e.g., `SELECT FOR UPDATE` on create)
- Auth: JWT (default) via `get_current_user` dependency

---

### 4. Layer Checklist (generate in this order)

| Layer | Path | Pattern |
|-------|------|---------|
| **Schema** | `backend/app/schemas/<entity>.py` | Pydantic v2: `Base`, `Update`, `Response`, `Create = Base` alias |
| **Model** | `backend/app/models/<entity>.py` | SQLAlchemy: UUID PK, `DateTime(timezone=True)`, minimal `__table_args__` |
| **CRUD** | `backend/app/crud/<entity>.py` | Async functions: `get`, `get_for_update`, `create`, `update`, `search`; or inherit `CRUDBase` |
| **Service** | `backend/app/services/<entity>.py` | Class with `db` injected; inherit `BaseService` with crud fn refs as static attrs; override only when business logic needed |
| **Router** | `backend/app/routers/<entity>.py` | FastAPI router, prefix `/api`, tag, `get_current_user` dep; use `paginated_response()` / `get_or_404()` helpers |
| **Router Registry** | `backend/app/main.py` | `app.include_router(entity_router, prefix="/api")` (no separate `__init__.py` registry) |
| **Migration** | `alembic revision --autogenerate -m "add <entity> table"` | Run `alembic upgrade head` |
| **Ingestion** | `backend/scripts/ingest.py` | Plain `ingest_<entity>()` function if CSV seeding needed |

---

### 5. Code Patterns to Follow

**Schema** (`schemas/<entity>.py`):
```python
class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    # ...

class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    # ...

class EntityResponse(EntityBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

# Create is just the base (no empty subclass)
EntityCreate = EntityBase
```

Use the generic `ListResponse[T]` from `app/schemas/__init__.py` — do not create a concrete `EntityListResponse` class.

**Model** (`models/<entity>.py`):
```python
class Entity(Base):
    __tablename__ = "<plural>"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    # ...
    # __table_args__ only for genuinely new indexes or composite constraints;
    # do not duplicate PK auto-index or unique-implied indexes
    __table_args__ = (UniqueConstraint("col_a", "col_b", name="uq_entity_ab"),)
```

Rules:
- UUID PK everywhere (`postgresql.UUID(as_uuid=True)`), no `index=True` on PK (auto-indexed)
- No `index=True` on `unique=True` columns (UNIQUE implies index)
- All `DateTime` columns: `DateTime(timezone=True)`, all code uses `datetime.now(timezone.utc)`

**CRUD** (`crud/<entity>.py`):
- Use `select()`, `select().where()`, `func.count()`
- `get_for_update` uses `.with_for_update()` for row locking
- Return tuples `(items, total)` for paginated searches
- Or inherit `CRUDBase[Model, CreateSchema, UpdateSchema]` from `app/crud/base.py`

**Service** (`services/<entity>.py`):
```python
class EntityService(BaseService):
    crud_get = staticmethod(get_entity)
    crud_get_for_update = staticmethod(get_entity_for_update)
    crud_search = staticmethod(search_entities)
    crud_create = staticmethod(create_entity)
    crud_update = staticmethod(update_entity)

    def __init__(self, db: AsyncSession):
        super().__init__(db)
```

Inherit `BaseService[Model, CreateSchema, UpdateSchema]` from `app/services/base.py`. Override methods only when real business logic is needed (e.g., booking stock management).

**Router** (`routers/<entity>.py`):
```python
router = APIRouter(prefix="/<plural>", tags=["<plural>"])

@router.get("", response_model=ListResponse[EntityResponse])
async def list_entities(
    q: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EntityService(db)
    skip = (page - 1) * page_size
    items, total = await service.search(q, skip, page_size)
    return paginated_response(items, total, page, page_size, EntityResponse)

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EntityService(db)
    return await get_or_404(entity_id, service.get)
```

Rules:
- Import helpers from `app.routers.utils`: `paginated_response`, `get_or_404`
- Return ORM models directly — rely on `ConfigDict(from_attributes=True)`, no manual `model_validate`
- `current_user` is required for authentication (valid JWT) but not used for authorization

**Main.py**: Add `app.include_router(entity_router, prefix="/api")`. No `init_db()`/`create_all` in lifespan — Alembic is the sole schema source.

---

### 6. Ingestion (if CSV seeding needed)

In `scripts/ingest.py`: add a plain async function `ingest_<entity>(db, fail_fast=False)` following the `ingestion_layer.md` rule. No `BaseHandler`, `HandlerRegistry`, or `ValidationError` class. CSV file at `backend/data/<entity>.csv`.

---

### 7. General Code Style
- **UUID PKs** everywhere (`postgresql.UUID(as_uuid=True)`)
- **Async** SQLAlchemy (`AsyncSession`, `await db.execute()`)
- **Pydantic v2** (`model_config = ConfigDict(from_attributes=True)`)
- **No raw SQL** — use SQLAlchemy ORM/select
- **Error handling**: raise `ValueError` in services, caught in routers → `HTTPException(400)`
- **Auth**: all routers use `current_user: dict = Depends(get_current_user)`
- **Error responses**: `AppException` subclasses (404, 409, 422) handled globally in `main.py`
