"""
Carrier model for trucking companies
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from pydantic import BaseModel, ConfigDict
from .load import Base


class Carrier(Base):
    """
    Carrier database model representing a trucking company
    """
    __tablename__ = "carriers"
    
    mc_number = Column(String, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    dot_number = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    # FMCSA verification status
    is_verified = Column(Boolean, default=False)
    fmcsa_status = Column(String, nullable=True)  # 'Active', 'Inactive', etc.
    last_verified_at = Column(DateTime, nullable=True)
    
    # Performance tracking
    total_loads = Column(Integer, default=0)
    successful_loads = Column(Integer, default=0)
    average_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Equipment capabilities
    equipment_types = Column(Text, nullable=True)  # JSON array of equipment types
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_at = Column(DateTime, nullable=True)


class CarrierCreate(BaseModel):
    """Pydantic model for creating a new carrier"""
    mc_number: str
    company_name: str
    dot_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    equipment_types: Optional[list[str]] = None


class CarrierUpdate(BaseModel):
    """Pydantic model for updating an existing carrier"""
    company_name: Optional[str] = None
    dot_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_verified: Optional[bool] = None
    fmcsa_status: Optional[str] = None
    equipment_types: Optional[list[str]] = None
    average_rating: Optional[int] = None


class CarrierResponse(BaseModel):
    """Pydantic model for carrier API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    mc_number: str
    company_name: str
    dot_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_verified: bool
    fmcsa_status: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    total_loads: int
    successful_loads: int
    average_rating: Optional[int] = None
    equipment_types: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime
    last_contact_at: Optional[datetime] = None


class FMCSAVerification(BaseModel):
    """Pydantic model for FMCSA verification response"""
    mc_number: str
    is_valid: bool
    status: str
    company_name: Optional[str] = None
    dot_number: Optional[str] = None
    error_message: Optional[str] = None