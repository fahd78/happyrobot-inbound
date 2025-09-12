"""
Call management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_database
from app.services.call_service import CallService
from app.models.call import CallCreate, CallUpdate, CallResponse, CallOutcome, CallSentiment, CallSummary
from app.core.security import verify_api_key

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call(
    call_data: CallCreate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Create a new call record"""
    call_service = CallService(db)
    
    # Check if call already exists
    existing_call = call_service.get_call(call_data.call_id)
    if existing_call:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Call with ID {call_data.call_id} already exists"
        )
    
    db_call = call_service.create_call(call_data)
    return CallResponse.model_validate(db_call)


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get a specific call by ID"""
    call_service = CallService(db)
    db_call = call_service.get_call(call_id)
    
    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call with ID {call_id} not found"
        )
    
    return CallResponse.model_validate(db_call)


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    call_update: CallUpdate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Update an existing call"""
    call_service = CallService(db)
    db_call = call_service.update_call(call_id, call_update)
    
    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call with ID {call_id} not found"
        )
    
    return CallResponse.model_validate(db_call)


@router.get("/carrier/{mc_number}", response_model=List[CallResponse])
async def get_calls_by_carrier(
    mc_number: str,
    skip: int = 0,
    limit: int = 100,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get calls for a specific carrier"""
    call_service = CallService(db)
    db_calls = call_service.get_calls_by_carrier(mc_number, skip=skip, limit=limit)
    
    return [CallResponse.model_validate(call) for call in db_calls]


@router.get("/", response_model=List[CallResponse])
async def get_recent_calls(
    limit: int = 50,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get recent calls across all carriers"""
    call_service = CallService(db)
    db_calls = call_service.get_recent_calls(limit=limit)
    
    return [CallResponse.model_validate(call) for call in db_calls]


@router.post("/{call_id}/end")
async def end_call(
    call_id: str,
    outcome: CallOutcome,
    sentiment: CallSentiment,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """End a call and set outcome/sentiment"""
    call_service = CallService(db)
    db_call = call_service.end_call(call_id, outcome, sentiment)
    
    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call with ID {call_id} not found"
        )
    
    return {
        "message": f"Call {call_id} ended",
        "outcome": outcome,
        "sentiment": sentiment,
        "call": CallResponse.model_validate(db_call)
    }


@router.post("/{call_id}/extract-data")
async def extract_call_data(
    call_id: str,
    extracted_data: dict,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Add extracted data from call analysis"""
    call_service = CallService(db)
    db_call = call_service.extract_call_data(call_id, extracted_data)
    
    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call with ID {call_id} not found"
        )
    
    return {
        "message": f"Data extracted for call {call_id}",
        "extracted_data": extracted_data,
        "call": CallResponse.model_validate(db_call)
    }


@router.get("/analytics/summary", response_model=CallSummary)
async def get_call_summary(
    days: int = 30,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get call analytics summary"""
    call_service = CallService(db)
    summary = call_service.get_call_summary(days=days)
    
    return summary


@router.post("/{call_id}/classify")
async def classify_call(
    call_id: str,
    transcript: Optional[str] = None,
    negotiation_successful: bool = False,
    carrier_verified: bool = False,
    loads_available: bool = False,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Classify call outcome and sentiment"""
    call_service = CallService(db)
    
    # Get the call to ensure it exists
    db_call = call_service.get_call(call_id)
    if not db_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call with ID {call_id} not found"
        )
    
    # Use transcript from call record if not provided
    if not transcript and db_call.transcript:
        transcript = db_call.transcript
    
    # Classify outcome and sentiment
    outcome = call_service.classify_call_outcome(
        transcript=transcript or "",
        negotiation_successful=negotiation_successful,
        carrier_verified=carrier_verified,
        loads_available=loads_available
    )
    
    sentiment = call_service.classify_call_sentiment(transcript or "")
    
    # Update call with classifications
    call_update = CallUpdate(
        outcome=outcome,
        sentiment=sentiment
    )
    
    if transcript and not db_call.transcript:
        call_update.transcript = transcript
    
    updated_call = call_service.update_call(call_id, call_update)
    
    return {
        "call_id": call_id,
        "outcome": outcome,
        "sentiment": sentiment,
        "call": CallResponse.model_validate(updated_call)
    }