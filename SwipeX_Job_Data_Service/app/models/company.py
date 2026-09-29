from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class CompanyType(str, Enum):
    MNC = "MNC"
    STARTUP = "Startup"
    NEWLY_FOUNDED = "Newly Founded"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    company_type = Column(
        SQLEnum(CompanyType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=CompanyType.STARTUP,
        nullable=False,
        index=True
    )
    is_newly_founded = Column(Boolean, default=False, nullable=False, index=True)
    industry = Column(String(100), nullable=False, default="Technology", index=True)
    headquarters = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    funding_stage = Column(String(50), nullable=True, default="Growth")  # e.g., "Seed", "Series A", "Bootstrapped", "Public"
    founded_year = Column(Integer, nullable=True)
    employee_count_range = Column(String(50), nullable=True)  # e.g., "1-10", "50-200", "10000+"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', type='{self.company_type}', newly_founded={self.is_newly_founded})>"
