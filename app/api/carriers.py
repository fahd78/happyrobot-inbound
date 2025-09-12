"""
Carrier management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_database
from app.services.carrier_service import CarrierService
from app.models.carrier import CarrierCreate, CarrierUpdate, CarrierResponse, FMCSAVerification
from app.core.security import verify_api_key

router = APIRouter(prefix="/carriers", tags=["carriers"])


@router.post("/", response_model=CarrierResponse, status_code=status.HTTP_201_CREATED)
async def create_carrier(
    carrier_data: CarrierCreate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Create a new carrier"""
    carrier_service = CarrierService(db)
    
    # Check if carrier already exists
    existing_carrier = carrier_service.get_carrier(carrier_data.mc_number)
    if existing_carrier:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Carrier with MC number {carrier_data.mc_number} already exists"
        )
    
    db_carrier = carrier_service.create_carrier(carrier_data)
    return CarrierResponse.model_validate(db_carrier)


@router.get("/{mc_number}", response_model=CarrierResponse)
async def get_carrier(
    mc_number: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get a specific carrier by MC number"""
    carrier_service = CarrierService(db)
    db_carrier = carrier_service.get_carrier(mc_number)
    
    if not db_carrier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carrier with MC number {mc_number} not found"
        )
    
    return CarrierResponse.model_validate(db_carrier)


@router.get("/", response_model=List[CarrierResponse])
async def get_carriers(
    skip: int = 0,
    limit: int = 100,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get multiple carriers with pagination"""
    carrier_service = CarrierService(db)
    db_carriers = carrier_service.get_carriers(skip=skip, limit=limit)
    
    return [CarrierResponse.model_validate(carrier) for carrier in db_carriers]


@router.put("/{mc_number}", response_model=CarrierResponse)
async def update_carrier(
    mc_number: str,
    carrier_update: CarrierUpdate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Update an existing carrier"""
    carrier_service = CarrierService(db)
    db_carrier = carrier_service.update_carrier(mc_number, carrier_update)
    
    if not db_carrier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carrier with MC number {mc_number} not found"
        )
    
    return CarrierResponse.model_validate(db_carrier)


@router.post("/{mc_number}/verify", response_model=FMCSAVerification)
async def verify_carrier(
    mc_number: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Verify carrier with FMCSA API"""
    carrier_service = CarrierService(db)
    verification = await carrier_service.verify_carrier_with_fmcsa(mc_number)
    
    return verification


@router.post("/{mc_number}/verify-and-update", response_model=CarrierResponse)
async def verify_and_update_carrier(
    mc_number: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Verify carrier with FMCSA and update database record"""
    carrier_service = CarrierService(db)
    db_carrier = await carrier_service.verify_and_update_carrier(mc_number)
    
    if not db_carrier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carrier verification failed for MC number {mc_number}"
        )
    
    return CarrierResponse.model_validate(db_carrier)


@router.post("/{mc_number}/contact")
async def record_contact(
    mc_number: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Record that a carrier was contacted"""
    carrier_service = CarrierService(db)
    db_carrier = carrier_service.record_call_contact(mc_number)
    
    if not db_carrier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carrier with MC number {mc_number} not found"
        )
    
    return {
        "message": f"Contact recorded for carrier {mc_number}",
        "last_contact_at": db_carrier.last_contact_at
    }


@router.get("/{mc_number}/equipment")
async def get_carrier_equipment(
    mc_number: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get carrier's equipment types"""
    carrier_service = CarrierService(db)
    equipment_types = carrier_service.get_carrier_equipment_types(mc_number)
    
    return {
        "mc_number": mc_number,
        "equipment_types": equipment_types
    }