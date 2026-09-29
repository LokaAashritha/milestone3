from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.company import CompanyType


class CompanyBase(BaseModel):
    name: str
    slug: str
    company_type: CompanyType
    is_newly_founded: bool = False
    industry: str = "Technology"
    headquarters: str
    funding_stage: Optional[str] = "Growth"
    logo_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count_range: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    companies: List[CompanyOut]
