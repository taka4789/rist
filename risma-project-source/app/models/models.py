from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime

from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default="user")  # user, manager, admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    lists = relationship("List", back_populates="owner")


class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    search_params = Column(JSON, nullable=True)  # キーワード、業種、住所などの検索条件
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_records = Column(Integer, default=0)
    
    owner = relationship("User", back_populates="lists")
    companies = relationship("Company", back_populates="list")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"))
    name = Column(String, index=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    industry_code = Column(String, nullable=True)
    prefecture = Column(String, nullable=True)
    city = Column(String, nullable=True)
    representative = Column(String, nullable=True)
    established_year = Column(Integer, nullable=True)
    capital = Column(Integer, nullable=True)  # 資本金（万円）
    employees = Column(Integer, nullable=True)  # 従業員数
    annual_revenue = Column(Integer, nullable=True)  # 売上高（万円）
    has_fax = Column(Boolean, default=False)
    has_contact_form = Column(Boolean, default=False)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    list = relationship("List", back_populates="companies")


class SearchJob(Base):
    __tablename__ = "search_jobs"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    job_type = Column(String)  # keyword, industry_location
    status = Column(String, default="pending")  # pending, processing, completed, failed
    params = Column(JSON)
    result_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
