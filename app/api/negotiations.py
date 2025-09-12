"""
Negotiation management API endpoints
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_database
from app.services.negotiation_service import NegotiationService
from app.models.negotiation import (
    NegotiationCreate, NegotiationUpdate, NegotiationResponse,
    NegotiationStatus, NegotiationDecision
)
from app.core.security import verify_api_key

router = APIRouter(prefix="/negotiations", tags=["negotiations"])


@router.post("/", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    negotiation_data: NegotiationCreate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Create a new negotiation"""
    negotiation_service = NegotiationService(db)
    
    # Check if negotiation already exists
    existing_negotiation = negotiation_service.get_negotiation(negotiation_data.negotiation_id)
    if existing_negotiation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Negotiation with ID {negotiation_data.negotiation_id} already exists"
        )
    
    db_negotiation = negotiation_service.create_negotiation(negotiation_data)
    return NegotiationResponse.model_validate(db_negotiation)


@router.get("/{negotiation_id}", response_model=NegotiationResponse)
async def get_negotiation(
    negotiation_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get a specific negotiation by ID"""
    negotiation_service = NegotiationService(db)
    db_negotiation = negotiation_service.get_negotiation(negotiation_id)
    
    if not db_negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Negotiation with ID {negotiation_id} not found"
        )
    
    return NegotiationResponse.model_validate(db_negotiation)


@router.get("/call/{call_id}/active", response_model=NegotiationResponse)
async def get_active_negotiation_for_call(
    call_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get active negotiation for a call"""
    negotiation_service = NegotiationService(db)
    db_negotiation = negotiation_service.get_active_negotiation_for_call(call_id)
    
    if not db_negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active negotiation found for call {call_id}"
        )
    
    return NegotiationResponse.model_validate(db_negotiation)


@router.get("/call/{call_id}/history", response_model=List[NegotiationResponse])
async def get_negotiation_history(
    call_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get all negotiations for a call"""
    negotiation_service = NegotiationService(db)
    db_negotiations = negotiation_service.get_negotiation_history(call_id)
    
    return [NegotiationResponse.model_validate(neg) for neg in db_negotiations]


@router.put("/{negotiation_id}", response_model=NegotiationResponse)
async def update_negotiation(
    negotiation_id: str,
    negotiation_update: NegotiationUpdate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Update an existing negotiation"""
    negotiation_service = NegotiationService(db)
    db_negotiation = negotiation_service.update_negotiation(negotiation_id, negotiation_update)
    
    if not db_negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Negotiation with ID {negotiation_id} not found"
        )
    
    return NegotiationResponse.model_validate(db_negotiation)


@router.post("/{negotiation_id}/counter-offer", response_model=NegotiationResponse)
async def make_counter_offer(
    negotiation_id: str,
    offer_amount: Decimal,
    offer_by: str,
    carrier_feedback: str = None,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Make a counter offer in negotiation"""
    negotiation_service = NegotiationService(db)
    db_negotiation = negotiation_service.make_counter_offer(
        negotiation_id, offer_amount, offer_by, carrier_feedback
    )
    
    if not db_negotiation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to make counter offer - negotiation may be inactive, expired, or at max rounds"
        )
    
    return NegotiationResponse.model_validate(db_negotiation)


@router.post("/{negotiation_id}/accept", response_model=NegotiationResponse)
async def accept_offer(
    negotiation_id: str,
    final_rate: Decimal,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Accept current offer and close negotiation"""
    negotiation_service = NegotiationService(db)
    db_negotiation = negotiation_service.accept_offer(negotiation_id, final_rate)
    
    if not db_negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Negotiation with ID {negotiation_id} not found"
        )
    
    return NegotiationResponse.model_validate(db_negotiation)


@router.post("/{negotiation_id}/reject", response_model=NegotiationResponse)
async def reject_offer(
    negotiation_id: str,
    reason: str = None,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Reject current offer and close negotiation"""
    negotiation_service = NegotiationService(db)
    db_negotiation = negotiation_service.reject_offer(negotiation_id, reason)
    
    if not db_negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Negotiation with ID {negotiation_id} not found"
        )
    
    return NegotiationResponse.model_validate(db_negotiation)


@router.post("/{negotiation_id}/evaluate", response_model=NegotiationDecision)
async def evaluate_carrier_offer(
    negotiation_id: str,
    carrier_offer: Decimal,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Evaluate carrier's counter offer and get decision"""
    negotiation_service = NegotiationService(db)
    decision = negotiation_service.evaluate_carrier_offer(negotiation_id, carrier_offer)
    
    return decision


@router.post("/cleanup-expired")
async def cleanup_expired_negotiations(
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Clean up expired negotiations"""
    negotiation_service = NegotiationService(db)
    expired_count = negotiation_service.cleanup_expired_negotiations()
    
    return {
        "message": f"Cleaned up {expired_count} expired negotiations"
    }