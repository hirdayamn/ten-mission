import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    booking_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    booking_reference = Column(String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))
    created_by = Column(String(255), nullable=False)
    cancelled_by = Column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_bookings_is_active", "is_active"),
    )

    member = relationship("Member", backref="bookings")
    inventory = relationship("Inventory", backref="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, ref='{self.booking_reference}', member={self.member_id}, inventory={self.inventory_id})>"