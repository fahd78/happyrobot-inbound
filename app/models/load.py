"""
Load model for freight shipments
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL as SQLDecimal, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, ConfigDict


Base = declarative_base()


class Load(Base):
    """
    Load database model representing a freight shipment
    """
    __tablename__ = "loads"
    
    # Required fields from specification
    load_id = Column(String, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    pickup_datetime = Column(DateTime, nullable=False)
    delivery_datetime = Column(DateTime, nullable=False)
    equipment_type = Column(String, nullable=False)
    loadboard_rate = Column(SQLDecimal(10, 2), nullable=False)
    notes = Column(Text)
    weight = Column(Integer)  # in pounds
    commodity_type = Column(String, nullable=False)
    num_of_pieces = Column(Integer)
    miles = Column(Integer)
    dimensions = Column(String)  # e.g., "48x53x102"
    
    # Additional tracking fields
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_carrier_mc = Column(String, nullable=True)
    final_rate = Column(SQLDecimal(10, 2), nullable=True)


class LoadCreate(BaseModel):
    """Pydantic model for creating a new load"""
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: Decimal
    notes: Optional[str] = None
    weight: Optional[int] = None
    commodity_type: str
    num_of_pieces: Optional[int] = None
    miles: Optional[int] = None
    dimensions: Optional[str] = None


class LoadUpdate(BaseModel):
    """Pydantic model for updating an existing load"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    pickup_datetime: Optional[datetime] = None
    delivery_datetime: Optional[datetime] = None
    equipment_type: Optional[str] = None
    loadboard_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    weight: Optional[int] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[int] = None
    dimensions: Optional[str] = None
    is_available: Optional[bool] = None
    assigned_carrier_mc: Optional[str] = None
    final_rate: Optional[Decimal] = None


class LoadResponse(BaseModel):
    """Pydantic model for load API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: Decimal
    notes: Optional[str] = None
    weight: Optional[int] = None
    commodity_type: str
    num_of_pieces: Optional[int] = None
    miles: Optional[int] = None
    dimensions: Optional[str] = None
    is_available: bool
    created_at: datetime
    updated_at: datetime
    assigned_carrier_mc: Optional[str] = None
    final_rate: Optional[Decimal] = None


class LoadMatch(BaseModel):
    """Pydantic model for load matching criteria"""
    origin_radius: Optional[int] = 100  # miles
    destination_radius: Optional[int] = 100  # miles
    equipment_types: Optional[list[str]] = None
    max_weight: Optional[int] = None
    min_rate: Optional[Decimal] = None
    max_rate: Optional[Decimal] = None
    pickup_date_range: Optional[int] = 7  # days from today