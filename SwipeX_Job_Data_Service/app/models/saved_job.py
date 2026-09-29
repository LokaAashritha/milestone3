from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(String(500), nullable=True)
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    job = relationship("Job", back_populates="saved_by_users")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),
    )

    def __repr__(self):
        return f"<SavedJob(id={self.id}, user_id='{self.user_id}', job_id={self.job_id})>"
