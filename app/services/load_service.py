"""
Service layer for load management operations
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.load import Load, LoadCreate, LoadUpdate, LoadMatch
from app.models.carrier import Carrier


class LoadService:
    """Service class for load-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_load(self, load_data: LoadCreate) -> Load:
        """
        Create a new load
        
        Args:
            load_data: Load creation data
            
        Returns:
            Load: Created load record
        """
        db_load = Load(**load_data.model_dump())
        self.db.add(db_load)
        self.db.commit()
        self.db.refresh(db_load)
        return db_load
    
    def get_load(self, load_id: str) -> Optional[Load]:
        """
        Get a load by ID
        
        Args:
            load_id: Load identifier
            
        Returns:
            Load: Load record or None if not found
        """
        return self.db.query(Load).filter(Load.load_id == load_id).first()
    
    def get_loads(self, skip: int = 0, limit: int = 100, available_only: bool = True) -> List[Load]:
        """
        Get multiple loads with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            available_only: Whether to filter for available loads only
            
        Returns:
            List[Load]: List of load records
        """
        query = self.db.query(Load)
        if available_only:
            query = query.filter(Load.is_available == True)
        
        return query.offset(skip).limit(limit).all()
    
    def update_load(self, load_id: str, load_update: LoadUpdate) -> Optional[Load]:
        """
        Update an existing load
        
        Args:
            load_id: Load identifier
            load_update: Updated load data
            
        Returns:
            Load: Updated load record or None if not found
        """
        db_load = self.get_load(load_id)
        if not db_load:
            return None
        
        update_data = load_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_load, field, value)
        
        db_load.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_load)
        return db_load
    
    def delete_load(self, load_id: str) -> bool:
        """
        Delete a load
        
        Args:
            load_id: Load identifier
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_load = self.get_load(load_id)
        if not db_load:
            return False
        
        self.db.delete(db_load)
        self.db.commit()
        return True
    
    def find_matching_loads(self, carrier_location: str, match_criteria: LoadMatch) -> List[Load]:
        """
        Find loads that match carrier criteria
        
        Args:
            carrier_location: Carrier's current location
            match_criteria: Load matching criteria
            
        Returns:
            List[Load]: List of matching available loads
        """
        query = self.db.query(Load).filter(Load.is_available == True)
        
        # Filter by equipment type if specified
        if match_criteria.equipment_types:
            query = query.filter(Load.equipment_type.in_(match_criteria.equipment_types))
        
        # Filter by weight if specified
        if match_criteria.max_weight:
            query = query.filter(or_(Load.weight.is_(None), Load.weight <= match_criteria.max_weight))
        
        # Filter by rate range if specified
        if match_criteria.min_rate:
            query = query.filter(Load.loadboard_rate >= match_criteria.min_rate)
        if match_criteria.max_rate:
            query = query.filter(Load.loadboard_rate <= match_criteria.max_rate)
        
        # Filter by pickup date range
        if match_criteria.pickup_date_range:
            cutoff_date = datetime.now() + timedelta(days=match_criteria.pickup_date_range)
            query = query.filter(Load.pickup_datetime <= cutoff_date)
        
        # Order by rate descending (highest paying first)
        query = query.order_by(Load.loadboard_rate.desc())
        
        return query.limit(10).all()  # Return top 10 matches
    
    def assign_load_to_carrier(self, load_id: str, carrier_mc: str, final_rate: float) -> Optional[Load]:
        """
        Assign a load to a carrier with final negotiated rate
        
        Args:
            load_id: Load identifier
            carrier_mc: Carrier MC number
            final_rate: Final negotiated rate
            
        Returns:
            Load: Updated load record or None if not found
        """
        update_data = LoadUpdate(
            assigned_carrier_mc=carrier_mc,
            final_rate=final_rate,
            is_available=False
        )
        return self.update_load(load_id, update_data)
    
    def get_load_summary_for_pitch(self, load_id: str) -> Optional[dict]:
        """
        Get formatted load information for AI agent to pitch to carrier
        
        Args:
            load_id: Load identifier
            
        Returns:
            dict: Formatted load summary for AI agent
        """
        load = self.get_load(load_id)
        if not load:
            return None
        
        return {
            "load_id": load.load_id,
            "route": f"{load.origin} to {load.destination}",
            "pickup_date": load.pickup_datetime.strftime("%B %d, %Y"),
            "delivery_date": load.delivery_datetime.strftime("%B %d, %Y"),
            "distance": f"{load.miles} miles" if load.miles else "Distance TBD",
            "equipment": load.equipment_type,
            "rate": f"${load.loadboard_rate:,.2f}",
            "commodity": load.commodity_type,
            "weight": f"{load.weight:,} lbs" if load.weight else "Weight TBD",
            "special_notes": load.notes or "No special requirements"
        }