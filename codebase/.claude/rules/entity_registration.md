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
- Auth: JWT (default) or API Key

---

### 4. Layer Checklist (generate in this order)

| Layer | Path | Pattern |
|-------|------|---------|
| **Schema** | `backend/app/schemas/<entity>.py` | Pydantic: `Base`, `Create`, `Update`, `Response`, `ListResponse` |
| **Model** | `backend/app/models/<entity>.py` | SQLAlchemy: UUID PK, indexes, `__table_args__` |
| **CRUD** | `backend/app/crud/<entity>.py` | Async functions: `get`, `list`, `create`, `update`, `search`, `get_for_update` |
| **Service** | `backend/app/services/<entity>.py` | Class with `db` injected; wraps CRUD + business logic |
| **Router** | `backend/app/routers/<entity>.py` | FastAPI router, prefix `/api`, tag, `get_current_user` dep |
| **Router Registry** | `backend/app/routers/__init__.py` | Export router; import in `main.py` |
| **Migration** | `alembic revision --autogenerate -m "add <entity> table"` | Run `alembic upgrade head` |
| **Ingestion** | `backend/scripts/ingest.py` | Add `Handler` + register in `HandlerRegistry` if CSV seeding needed |

---

### 5. Code Patterns to Follow

**Schema** (`schemas/<entity>.py`):
```python
class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    # ...

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    # ...

class EntityResponse(EntityBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class EntityListResponse(BaseModel):
    items: list[EntityResponse]
    total: int
    page: int
    page_size: int
```

**Model** (`models/<entity>.py`):
```python
class Entity(Base):
    __tablename__ = "<plural>"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    # ...
    __table_args__ = (Index("ix_entity_name", "name"),)
```

**CRUD** (`crud/<entity>.py`):
- Use `select()`, `select().where()`, `func.count()`
- `get_for_update` uses `.with_for_update()` for row locking
- Return tuples `(items, total)` for paginated searches

**Service** (`services/<entity>.py`):
```python
class EntityService:
    def __init__(self, db: AsyncSession):
        self.db = db
    async def create(self, data): ...
    async def search(self, q, skip, limit): ...
```

**Router** (`routers/<entity>.py`):
```python
router = APIRouter(prefix="/<plural>", tags=["<plural>"])

@router.get("", response_model=EntityListResponse)
async def list_entities(q: Optional[str]=None, page=1, page_size=20, db=Depends(get_db), user=Depends(get_current_user)):
    ...
```

**Main.py**: Add import and `app.include_router(entity_router, prefix="/api")`

---

### 6. Ingestion Registry (if CSV seeding needed)

In `scripts/ingest.py`:
1. Add `EntityHandler(BaseHandler)` with `get_csv_filename`, `parse_row`, `process_all`
2. Use bulk upsert pattern: fetch existing by unique key → split create/update → `db.add_all()` + flush
3. Register: `registry.register("<entity>", EntityHandler)`

---

### 7. General Code Style
- **UUID PKs** everywhere (`postgresql.UUID(as_uuid=True)`)
- **Async** SQLAlchemy (`AsyncSession`, `await db.execute()`)
- **Pydantic v2** (`model_config = ConfigDict(from_attributes=True)`)
- **No raw SQL** — use SQLAlchemy ORM/select
- **Error handling**: raise `ValueError` in services, caught in routers → `HTTPException(400)`
- **Auth**: all routers use `current_user: dict = Depends(get_current_user)`