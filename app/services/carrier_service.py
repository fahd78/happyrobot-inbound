"""
Service layer for carrier management and FMCSA verification
"""
import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import httpx
from app.models.carrier import Carrier, CarrierCreate, CarrierUpdate, FMCSAVerification
from app.core.config import settings


class CarrierService:
    """Service class for carrier-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_carrier(self, carrier_data: CarrierCreate) -> Carrier:
        """
        Create a new carrier
        
        Args:
            carrier_data: Carrier creation data
            
        Returns:
            Carrier: Created carrier record
        """
        # Convert equipment_types list to JSON string for storage
        carrier_dict = carrier_data.model_dump()
        if carrier_dict.get('equipment_types'):
            carrier_dict['equipment_types'] = json.dumps(carrier_dict['equipment_types'])
        
        db_carrier = Carrier(**carrier_dict)
        self.db.add(db_carrier)
        self.db.commit()
        self.db.refresh(db_carrier)
        return db_carrier
    
    def get_carrier(self, mc_number: str) -> Optional[Carrier]:
        """
        Get a carrier by MC number
        
        Args:
            mc_number: Carrier MC number
            
        Returns:
            Carrier: Carrier record or None if not found
        """
        return self.db.query(Carrier).filter(Carrier.mc_number == mc_number).first()
    
    def get_carriers(self, skip: int = 0, limit: int = 100) -> List[Carrier]:
        """
        Get multiple carriers with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Carrier]: List of carrier records
        """
        return self.db.query(Carrier).offset(skip).limit(limit).all()
    
    def update_carrier(self, mc_number: str, carrier_update: CarrierUpdate) -> Optional[Carrier]:
        """
        Update an existing carrier
        
        Args:
            mc_number: Carrier MC number
            carrier_update: Updated carrier data
            
        Returns:
            Carrier: Updated carrier record or None if not found
        """
        db_carrier = self.get_carrier(mc_number)
        if not db_carrier:
            return None
        
        update_data = carrier_update.model_dump(exclude_unset=True)
        
        # Handle equipment_types conversion
        if 'equipment_types' in update_data and update_data['equipment_types']:
            update_data['equipment_types'] = json.dumps(update_data['equipment_types'])
        
        for field, value in update_data.items():
            setattr(db_carrier, field, value)
        
        db_carrier.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_carrier)
        return db_carrier
    
    async def verify_carrier_with_fmcsa(self, mc_number: str) -> FMCSAVerification:
        """
        Verify carrier with FMCSA API
        
        Args:
            mc_number: Carrier MC number to verify
            
        Returns:
            FMCSAVerification: Verification result
        """
        # Mock FMCSA verification for demo purposes
        # In production, integrate with actual FMCSA API
        mock_carriers = {
            "123456": {"company": "ABC Trucking LLC", "dot": "987654", "status": "ACTIVE"},
            "789012": {"company": "XYZ Transport Inc", "dot": "555666", "status": "ACTIVE"},
            "456789": {"company": "Best Freight Co", "dot": "111222", "status": "ACTIVE"},
            "999888": {"company": "Demo Carrier Ltd", "dot": "333444", "status": "ACTIVE"}
        }
        
        if mc_number in mock_carriers:
            carrier_info = mock_carriers[mc_number]
            return FMCSAVerification(
                mc_number=mc_number,
                is_valid=True,
                status="ACTIVE",
                company_name=carrier_info["company"],
                dot_number=carrier_info["dot"]
            )
        else:
            return FMCSAVerification(
                mc_number=mc_number,
                is_valid=True,  # Allow unknown carriers for demo
                status="ACTIVE",
                company_name=f"Carrier {mc_number}",
                dot_number=f"DOT{mc_number}"
            )
    
    async def verify_and_update_carrier(self, mc_number: str) -> Optional[Carrier]:
        """
        Verify carrier with FMCSA and update database record
        
        Args:
            mc_number: Carrier MC number
            
        Returns:
            Carrier: Updated carrier record or None if not found
        """
        # Get or create carrier record
        carrier = self.get_carrier(mc_number)
        
        # Verify with FMCSA
        verification = await self.verify_carrier_with_fmcsa(mc_number)
        
        if not carrier and verification.is_valid:
            # Create new carrier if verification successful and not in database
            carrier_data = CarrierCreate(
                mc_number=mc_number,
                company_name=verification.company_name or "Unknown Company",
                dot_number=verification.dot_number
            )
            carrier = self.create_carrier(carrier_data)
        
        if carrier:
            # Update existing carrier with verification results
            update_data = CarrierUpdate(
                is_verified=verification.is_valid,
                fmcsa_status=verification.status
            )
            
            if verification.company_name and not carrier.company_name:
                update_data.company_name = verification.company_name
            
            if verification.dot_number and not carrier.dot_number:
                update_data.dot_number = verification.dot_number
            
            carrier = self.update_carrier(mc_number, update_data)
            carrier.last_verified_at = datetime.utcnow()
            self.db.commit()
        
        return carrier
    
    def record_call_contact(self, mc_number: str) -> Optional[Carrier]:
        """
        Record that a carrier was contacted
        
        Args:
            mc_number: Carrier MC number
            
        Returns:
            Carrier: Updated carrier record or None if not found
        """
        carrier = self.get_carrier(mc_number)
        if carrier:
            carrier.last_contact_at = datetime.utcnow()
            self.db.commit()
        return carrier
    
    def get_carrier_equipment_types(self, mc_number: str) -> List[str]:
        """
        Get carrier's equipment types
        
        Args:
            mc_number: Carrier MC number
            
        Returns:
            List[str]: List of equipment types
        """
        carrier = self.get_carrier(mc_number)
        if carrier and carrier.equipment_types:
            try:
                return json.loads(carrier.equipment_types)
            except json.JSONDecodeError:
                return []
        return []