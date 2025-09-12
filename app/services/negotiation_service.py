"""
Service layer for negotiation management and pricing logic
"""
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.negotiation import (
    Negotiation, NegotiationCreate, NegotiationUpdate, 
    NegotiationStatus, OfferType, NegotiationDecision
)


class NegotiationService:
    """Service class for negotiation-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_negotiation(self, negotiation_data: NegotiationCreate) -> Negotiation:
        """
        Create a new negotiation
        
        Args:
            negotiation_data: Negotiation creation data
            
        Returns:
            Negotiation: Created negotiation record
        """
        db_negotiation = Negotiation(**negotiation_data.model_dump())
        # Set expiration time (24 hours from creation)
        db_negotiation.expires_at = datetime.utcnow() + timedelta(hours=24)
        
        self.db.add(db_negotiation)
        self.db.commit()
        self.db.refresh(db_negotiation)
        return db_negotiation
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Negotiation]:
        """
        Get a negotiation by ID
        
        Args:
            negotiation_id: Negotiation identifier
            
        Returns:
            Negotiation: Negotiation record or None if not found
        """
        return self.db.query(Negotiation).filter(
            Negotiation.negotiation_id == negotiation_id
        ).first()
    
    def get_active_negotiation_for_call(self, call_id: str) -> Optional[Negotiation]:
        """
        Get active negotiation for a call
        
        Args:
            call_id: Call identifier
            
        Returns:
            Negotiation: Active negotiation or None if not found
        """
        return self.db.query(Negotiation).filter(
            Negotiation.call_id == call_id,
            Negotiation.status == NegotiationStatus.ACTIVE
        ).first()
    
    def update_negotiation(self, negotiation_id: str, 
                          negotiation_update: NegotiationUpdate) -> Optional[Negotiation]:
        """
        Update an existing negotiation
        
        Args:
            negotiation_id: Negotiation identifier
            negotiation_update: Updated negotiation data
            
        Returns:
            Negotiation: Updated negotiation record or None if not found
        """
        db_negotiation = self.get_negotiation(negotiation_id)
        if not db_negotiation:
            return None
        
        update_data = negotiation_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_negotiation, field, value)
        
        db_negotiation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_negotiation)
        return db_negotiation
    
    def make_counter_offer(self, negotiation_id: str, offer_amount: Decimal, 
                          offer_by: str, carrier_feedback: str = None) -> Optional[Negotiation]:
        """
        Make a counter offer in negotiation
        
        Args:
            negotiation_id: Negotiation identifier
            offer_amount: New offer amount
            offer_by: Who is making the offer ('broker' or 'carrier')
            carrier_feedback: Optional feedback from carrier
            
        Returns:
            Negotiation: Updated negotiation or None if not found/invalid
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation or negotiation.status != NegotiationStatus.ACTIVE:
            return None
        
        # Check if negotiation has expired
        if negotiation.expires_at and negotiation.expires_at < datetime.utcnow():
            self.update_negotiation(negotiation_id, 
                                  NegotiationUpdate(status=NegotiationStatus.EXPIRED))
            return None
        
        # Check if max rounds exceeded
        if negotiation.current_round >= negotiation.max_rounds:
            self.update_negotiation(negotiation_id, 
                                  NegotiationUpdate(status=NegotiationStatus.REJECTED))
            return None
        
        # Update with counter offer
        update_data = NegotiationUpdate(
            current_round=negotiation.current_round + 1,
            current_offer_amount=offer_amount,
            current_offer_by=offer_by,
            current_offer_type=OfferType.COUNTER
        )
        
        if carrier_feedback:
            update_data.carrier_feedback = carrier_feedback
        
        return self.update_negotiation(negotiation_id, update_data)
    
    def accept_offer(self, negotiation_id: str, final_rate: Decimal) -> Optional[Negotiation]:
        """
        Accept current offer and close negotiation
        
        Args:
            negotiation_id: Negotiation identifier
            final_rate: Final agreed rate
            
        Returns:
            Negotiation: Updated negotiation or None if not found
        """
        update_data = NegotiationUpdate(
            status=NegotiationStatus.ACCEPTED,
            final_agreed_rate=final_rate,
            current_offer_type=OfferType.FINAL
        )
        return self.update_negotiation(negotiation_id, update_data)
    
    def reject_offer(self, negotiation_id: str, reason: str = None) -> Optional[Negotiation]:
        """
        Reject current offer and close negotiation
        
        Args:
            negotiation_id: Negotiation identifier
            reason: Optional rejection reason
            
        Returns:
            Negotiation: Updated negotiation or None if not found
        """
        update_data = NegotiationUpdate(
            status=NegotiationStatus.REJECTED
        )
        
        if reason:
            update_data.broker_notes = reason
        
        return self.update_negotiation(negotiation_id, update_data)
    
    def evaluate_carrier_offer(self, negotiation_id: str, 
                              carrier_offer: Decimal) -> NegotiationDecision:
        """
        Evaluate carrier's counter offer and decide response
        
        Args:
            negotiation_id: Negotiation identifier
            carrier_offer: Carrier's offer amount
            
        Returns:
            NegotiationDecision: Decision on how to respond
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            return NegotiationDecision(
                should_accept=False,
                reasoning="Negotiation not found",
                is_final_offer=True
            )
        
        original_rate = negotiation.original_rate
        current_round = negotiation.current_round
        max_rounds = negotiation.max_rounds
        
        # Calculate acceptable thresholds
        # Accept if offer is within 5% of original rate
        min_acceptable = original_rate * Decimal("0.95")
        
        # Be more flexible in later rounds
        if current_round >= max_rounds - 1:
            min_acceptable = original_rate * Decimal("0.90")  # 10% discount max
        
        if carrier_offer >= min_acceptable:
            return NegotiationDecision(
                should_accept=True,
                reasoning=f"Offer ${carrier_offer} is acceptable (within threshold)",
                is_final_offer=True
            )
        
        # If we're at max rounds, make final offer
        if current_round >= max_rounds:
            return NegotiationDecision(
                should_accept=False,
                counter_offer_amount=min_acceptable,
                reasoning=f"Final offer at minimum acceptable rate ${min_acceptable}",
                is_final_offer=True
            )
        
        # Calculate counter offer (split the difference)
        counter_offer = (carrier_offer + original_rate) / 2
        counter_offer = max(counter_offer, min_acceptable)  # Don't go below minimum
        
        return NegotiationDecision(
            should_accept=False,
            counter_offer_amount=counter_offer,
            reasoning=f"Counter-offering ${counter_offer} (round {current_round + 1})",
            is_final_offer=False
        )
    
    def get_negotiation_history(self, call_id: str) -> List[Negotiation]:
        """
        Get all negotiations for a call
        
        Args:
            call_id: Call identifier
            
        Returns:
            List[Negotiation]: List of negotiations for the call
        """
        return (self.db.query(Negotiation)
                .filter(Negotiation.call_id == call_id)
                .order_by(Negotiation.created_at.desc())
                .all())
    
    def cleanup_expired_negotiations(self) -> int:
        """
        Clean up expired negotiations
        
        Returns:
            int: Number of negotiations expired
        """
        expired_negotiations = (self.db.query(Negotiation)
                               .filter(
                                   Negotiation.status == NegotiationStatus.ACTIVE,
                                   Negotiation.expires_at < datetime.utcnow()
                               )
                               .all())
        
        for negotiation in expired_negotiations:
            negotiation.status = NegotiationStatus.EXPIRED
            negotiation.updated_at = datetime.utcnow()
        
        self.db.commit()
        return len(expired_negotiations)