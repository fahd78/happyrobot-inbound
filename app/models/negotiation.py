"""
Negotiation model for tracking pricing back-and-forth
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum
from sqlalchemy import Column, String, DateTime, DECIMAL as SQLDecimal, Integer, Enum as SQLEnum, Text
from pydantic import BaseModel, ConfigDict
from .load import Base


class NegotiationStatus(str, Enum):
    """Enumeration of negotiation statuses"""
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OfferType(str, Enum):
    """Enumeration of offer types"""
    INITIAL = "initial"
    COUNTER = "counter"
    FINAL = "final"


class Negotiation(Base):
    """
    Negotiation database model for tracking pricing negotiations
    """
    __tablename__ = "negotiations"
    
    negotiation_id = Column(String, primary_key=True, index=True)
    call_id = Column(String, nullable=False, index=True)
    load_id = Column(String, nullable=False, index=True)
    carrier_mc_number = Column(String, nullable=False)
    
    # Current negotiation state
    status = Column(SQLEnum(NegotiationStatus), default=NegotiationStatus.ACTIVE)
    current_round = Column(Integer, default=1)
    max_rounds = Column(Integer, default=3)
    
    # Current offer details
    current_offer_amount = Column(SQLDecimal(10, 2), nullable=False)
    current_offer_by = Column(String, nullable=False)  # 'broker' or 'carrier'
    current_offer_type = Column(SQLEnum(OfferType), nullable=False)
    
    # Original loadboard rate
    original_rate = Column(SQLDecimal(10, 2), nullable=False)
    
    # Final agreement
    final_agreed_rate = Column(SQLDecimal(10, 2), nullable=True)
    
    # Notes and reasoning
    broker_notes = Column(Text, nullable=True)
    carrier_feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class NegotiationCreate(BaseModel):
    """Pydantic model for creating a new negotiation"""
    negotiation_id: str
    call_id: str
    load_id: str
    carrier_mc_number: str
    current_offer_amount: Decimal
    current_offer_by: str
    current_offer_type: OfferType
    original_rate: Decimal
    max_rounds: Optional[int] = 3


class NegotiationUpdate(BaseModel):
    """Pydantic model for updating a negotiation"""
    status: Optional[NegotiationStatus] = None
    current_round: Optional[int] = None
    current_offer_amount: Optional[Decimal] = None
    current_offer_by: Optional[str] = None
    current_offer_type: Optional[OfferType] = None
    final_agreed_rate: Optional[Decimal] = None
    broker_notes: Optional[str] = None
    carrier_feedback: Optional[str] = None
    expires_at: Optional[datetime] = None


class NegotiationResponse(BaseModel):
    """Pydantic model for negotiation API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    negotiation_id: str
    call_id: str
    load_id: str
    carrier_mc_number: str
    status: NegotiationStatus
    current_round: int
    max_rounds: int
    current_offer_amount: Decimal
    current_offer_by: str
    current_offer_type: OfferType
    original_rate: Decimal
    final_agreed_rate: Optional[Decimal] = None
    broker_notes: Optional[str] = None
    carrier_feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class NegotiationDecision(BaseModel):
    """Pydantic model for AI negotiation decision"""
    should_accept: bool
    counter_offer_amount: Optional[Decimal] = None
    reasoning: str
    is_final_offer: bool = False