from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum, Integer, DECIMAL as SQLDecimal, JSON
from pydantic import BaseModel, ConfigDict
from .load import Base


class CallOutcome(str, Enum):
    SUCCESSFUL_BOOKING = "successful_booking"
    REJECTED_BY_CARRIER = "rejected_by_carrier" 
    FAILED_VERIFICATION = "failed_verification"
    NO_SUITABLE_LOADS = "no_suitable_loads"
    NEGOTIATION_FAILED = "negotiation_failed"
    TRANSFERRED_TO_SALES = "transferred_to_sales"
    CALL_DROPPED = "call_dropped"
    SYSTEM_ERROR = "system_error"


class CallSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    SATISFIED = "satisfied"


class Call(Base):
    __tablename__ = "calls"
    
    call_id = Column(String, primary_key=True, index=True)
    carrier_mc_number = Column(String, nullable=False, index=True)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    happyrobot_call_id = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    
    discussed_load_id = Column(String, nullable=True)
    initial_rate_offered = Column(SQLDecimal(10, 2), nullable=True)
    final_negotiated_rate = Column(SQLDecimal(10, 2), nullable=True)
    
    outcome = Column(SQLEnum(CallOutcome), nullable=True)
    sentiment = Column(SQLEnum(CallSentiment), nullable=True)
    
    extracted_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CallCreate(BaseModel):
    call_id: str
    carrier_mc_number: str
    start_time: datetime
    happyrobot_call_id: Optional[str] = None


class CallUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    discussed_load_id: Optional[str] = None
    initial_rate_offered: Optional[Decimal] = None
    final_negotiated_rate: Optional[Decimal] = None
    outcome: Optional[CallOutcome] = None
    sentiment: Optional[CallSentiment] = None
    extracted_data: Optional[Dict[str, Any]] = None


class CallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    call_id: str
    carrier_mc_number: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    happyrobot_call_id: Optional[str] = None
    transcript: Optional[str] = None
    discussed_load_id: Optional[str] = None
    initial_rate_offered: Optional[Decimal] = None
    final_negotiated_rate: Optional[Decimal] = None
    outcome: Optional[CallOutcome] = None
    sentiment: Optional[CallSentiment] = None
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class CallSummary(BaseModel):
    total_calls: int
    successful_bookings: int
    average_duration: Optional[float] = None
    sentiment_breakdown: Dict[CallSentiment, int]
    outcome_breakdown: Dict[CallOutcome, int]
    conversion_rate: float