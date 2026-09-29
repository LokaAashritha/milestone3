from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class SwipeDirection(str, Enum):
    RIGHT = "right"  # Apply / Save / Like
    LEFT = "left"    # Skip / Pass


class SwipeActionType(str, Enum):
    APPLY = "apply"
    SAVE = "save"
    SKIP = "skip"


class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    direction = Column(
        SQLEnum(SwipeDirection, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False
    )
    action_type = Column(
        SQLEnum(SwipeActionType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=SwipeActionType.APPLY
    )
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    job = relationship("Job", back_populates="swipes")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_swipe"),
    )

    def __repr__(self):
        return f"<Swipe(id={self.id}, user_id='{self.user_id}', job_id={self.job_id}, direction='{self.direction}')>"
