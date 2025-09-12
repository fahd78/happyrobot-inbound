"""
Load management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_database
from app.services.load_service import LoadService
from app.models.load import LoadCreate, LoadUpdate, LoadResponse, LoadMatch
from app.core.security import verify_api_key

router = APIRouter(prefix="/loads", tags=["loads"])


@router.post("/", response_model=LoadResponse, status_code=status.HTTP_201_CREATED)
async def create_load(
    load_data: LoadCreate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Create a new load"""
    load_service = LoadService(db)
    
    # Check if load already exists
    existing_load = load_service.get_load(load_data.load_id)
    if existing_load:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Load with ID {load_data.load_id} already exists"
        )
    
    db_load = load_service.create_load(load_data)
    return LoadResponse.model_validate(db_load)


@router.get("/{load_id}", response_model=LoadResponse)
async def get_load(
    load_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get a specific load by ID"""
    load_service = LoadService(db)
    db_load = load_service.get_load(load_id)
    
    if not db_load:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Load with ID {load_id} not found"
        )
    
    return LoadResponse.model_validate(db_load)


@router.get("/", response_model=List[LoadResponse])
async def get_loads(
    skip: int = 0,
    limit: int = 100,
    available_only: bool = True,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get multiple loads with pagination"""
    load_service = LoadService(db)
    db_loads = load_service.get_loads(skip=skip, limit=limit, available_only=available_only)
    
    return [LoadResponse.model_validate(load) for load in db_loads]


@router.put("/{load_id}", response_model=LoadResponse)
async def update_load(
    load_id: str,
    load_update: LoadUpdate,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Update an existing load"""
    load_service = LoadService(db)
    db_load = load_service.update_load(load_id, load_update)
    
    if not db_load:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Load with ID {load_id} not found"
        )
    
    return LoadResponse.model_validate(db_load)


@router.delete("/{load_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_load(
    load_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Delete a load"""
    load_service = LoadService(db)
    success = load_service.delete_load(load_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Load with ID {load_id} not found"
        )


@router.post("/search", response_model=List[LoadResponse])
async def search_loads(
    carrier_location: str,
    match_criteria: LoadMatch,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Find loads matching carrier criteria"""
    load_service = LoadService(db)
    matching_loads = load_service.find_matching_loads(carrier_location, match_criteria)
    
    return [LoadResponse.model_validate(load) for load in matching_loads]


@router.get("/{load_id}/summary")
async def get_load_summary(
    load_id: str,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Get formatted load summary for AI agent"""
    load_service = LoadService(db)
    summary = load_service.get_load_summary_for_pitch(load_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Load with ID {load_id} not found"
        )
    
    return summary


@router.post("/{load_id}/assign")
async def assign_load(
    load_id: str,
    carrier_mc: str,
    final_rate: float,
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_database)
):
    """Assign load to carrier with final negotiated rate"""
    load_service = LoadService(db)
    db_load = load_service.assign_load_to_carrier(load_id, carrier_mc, final_rate)
    
    if not db_load:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Load with ID {load_id} not found"
        )
    
    return {
        "message": f"Load {load_id} assigned to carrier {carrier_mc}",
        "final_rate": final_rate,
        "load": LoadResponse.model_validate(db_load)
    }