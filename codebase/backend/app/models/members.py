import uuid
from sqlalchemy import Column, Integer, String, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    booking_count = Column(Integer, nullable=False, default=0)
    joining_date = Column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("first_name", "last_name", "joining_date", name="uq_member_name_date"),
        Index("ix_members_full_name", "full_name"),
    )

    def __repr__(self):
        return f"<Member(id={self.id}, username='{self.username}', name='{self.full_name}', bookings={self.booking_count})>"