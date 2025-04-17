from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "user"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None


class ListBase(BaseModel):
    title: str
    description: Optional[str] = None
    search_params: Optional[Dict[str, Any]] = None


class ListCreate(ListBase):
    pass


class ListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    search_params: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ListInDBBase(ListBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    status: str
    total_records: int

    class Config:
        orm_mode = True


class List(ListInDBBase):
    pass


class CompanyBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    representative: Optional[str] = None
    established_year: Optional[int] = None
    capital: Optional[int] = None
    employees: Optional[int] = None
    annual_revenue: Optional[int] = None
    has_fax: Optional[bool] = False
    has_contact_form: Optional[bool] = False
    source_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    list_id: int


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    representative: Optional[str] = None
    established_year: Optional[int] = None
    capital: Optional[int] = None
    employees: Optional[int] = None
    annual_revenue: Optional[int] = None
    has_fax: Optional[bool] = None
    has_contact_form: Optional[bool] = None
    source_url: Optional[str] = None


class CompanyInDBBase(CompanyBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Company(CompanyInDBBase):
    pass


class SearchJobBase(BaseModel):
    job_type: str
    params: Dict[str, Any]


class SearchJobCreate(SearchJobBase):
    list_id: int


class SearchJobUpdate(BaseModel):
    status: Optional[str] = None
    result_count: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class SearchJobInDBBase(SearchJobBase):
    id: int
    list_id: int
    user_id: int
    status: str
    result_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SearchJob(SearchJobInDBBase):
    pass


class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


class AuditLog(AuditLogCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class KeywordSearchParams(BaseModel):
    keywords: List[str] = Field(..., min_items=1)
    exclude_keywords: Optional[List[str]] = None
    max_results: Optional[int] = 1000


class IndustryLocationSearchParams(BaseModel):
    industry_codes: List[str] = Field(..., min_items=1)
    prefectures: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    max_results: Optional[int] = 1000


class ExportFormat(BaseModel):
    format: str = Field(..., regex='^(csv|excel|json)$')
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
