import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    remaining_count = Column(Integer, nullable=False, default=0)
    expiration_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("title", "expiration_date", name="uq_inventory_title_expiration"),
    )

    def __repr__(self):
        return f"<Inventory(id={self.id}, title='{self.title}', remaining={self.remaining_count}, active={self.is_active})>"