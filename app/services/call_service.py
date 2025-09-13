"""
Service layer for call management and tracking
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import structlog
from app.models.call import Call, CallCreate, CallUpdate, CallOutcome, CallSentiment, CallSummary

logger = structlog.get_logger()


class CallService:
    """Service class for call-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_call(self, call_data: CallCreate) -> Call:
        """
        Create a new call record
        
        Args:
            call_data: Call creation data
            
        Returns:
            Call: Created call record
        """
        db_call = Call(**call_data.model_dump())
        self.db.add(db_call)
        self.db.commit()
        self.db.refresh(db_call)
        return db_call
    
    def get_call(self, call_id: str) -> Optional[Call]:
        """
        Get a call by ID
        
        Args:
            call_id: Call identifier
            
        Returns:
            Call: Call record or None if not found
        """
        return self.db.query(Call).filter(Call.call_id == call_id).first()
    
    def get_calls_by_carrier(self, mc_number: str, skip: int = 0, limit: int = 100) -> List[Call]:
        """
        Get calls for a specific carrier
        
        Args:
            mc_number: Carrier MC number
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Call]: List of call records
        """
        return (self.db.query(Call)
                .filter(Call.carrier_mc_number == mc_number)
                .order_by(Call.start_time.desc())
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_recent_calls(self, limit: int = 50) -> List[Call]:
        """
        Get recent calls across all carriers
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List[Call]: List of recent call records
        """
        return (self.db.query(Call)
                .order_by(Call.start_time.desc())
                .limit(limit)
                .all())
    
    def update_call(self, call_id: str, call_update: CallUpdate) -> Optional[Call]:
        """
        Update an existing call
        
        Args:
            call_id: Call identifier
            call_update: Updated call data
            
        Returns:
            Call: Updated call record or None if not found
        """
        db_call = self.get_call(call_id)
        if not db_call:
            return None
        
        update_data = call_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_call, field, value)
        
        db_call.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_call)
        return db_call
    
    def end_call(self, call_id: str, outcome: CallOutcome, sentiment: CallSentiment) -> Optional[Call]:
        """
        End a call and set outcome/sentiment
        
        Args:
            call_id: Call identifier
            outcome: Call outcome
            sentiment: Call sentiment
            
        Returns:
            Call: Updated call record or None if not found
        """
        db_call = self.get_call(call_id)
        if not db_call:
            return None
        
        end_time = datetime.utcnow()
        duration = int((end_time - db_call.start_time).total_seconds()) if db_call.start_time else None
        
        update_data = CallUpdate(
            end_time=end_time,
            duration_seconds=duration,
            outcome=outcome,
            sentiment=sentiment
        )
        
        return self.update_call(call_id, update_data)
    
    def extract_call_data(self, call_id: str, extracted_data: Dict[str, Any]) -> Optional[Call]:
        """
        Add extracted data from call analysis
        
        Args:
            call_id: Call identifier
            extracted_data: Structured data extracted from call
            
        Returns:
            Call: Updated call record or None if not found
        """
        update_data = CallUpdate(extracted_data=extracted_data)
        return self.update_call(call_id, update_data)
    
    def get_call_summary(self, days: int = 30) -> CallSummary:
        """
        Get call analytics summary
        
        Args:
            days: Number of days to include in summary
            
        Returns:
            CallSummary: Analytics summary
        """
        # Get date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query for the time period
        base_query = self.db.query(Call).filter(Call.start_time >= cutoff_date)
        
        # Total calls
        total_calls = base_query.count()
        
        # Successful bookings
        successful_bookings = (base_query
                             .filter(Call.outcome == CallOutcome.SUCCESSFUL_BOOKING)
                             .count())
        
        # Average duration (excluding None values)
        avg_duration_result = (base_query
                              .filter(Call.duration_seconds.isnot(None))
                              .with_entities(func.avg(Call.duration_seconds))
                              .scalar())
        avg_duration = float(avg_duration_result) if avg_duration_result else None
        
        # Sentiment breakdown
        sentiment_data = (base_query
                         .filter(Call.sentiment.isnot(None))
                         .with_entities(Call.sentiment, func.count(Call.sentiment))
                         .group_by(Call.sentiment)
                         .all())
        
        sentiment_breakdown = {
            sentiment: count for sentiment, count in sentiment_data
        }
        
        # Outcome breakdown
        outcome_data = (base_query
                       .filter(Call.outcome.isnot(None))
                       .with_entities(Call.outcome, func.count(Call.outcome))
                       .group_by(Call.outcome)
                       .all())
        
        outcome_breakdown = {
            outcome: count for outcome, count in outcome_data
        }
        
        # Conversion rate
        conversion_rate = (successful_bookings / total_calls * 100) if total_calls > 0 else 0.0
        
        return CallSummary(
            total_calls=total_calls,
            successful_bookings=successful_bookings,
            average_duration=avg_duration,
            sentiment_breakdown=sentiment_breakdown,
            outcome_breakdown=outcome_breakdown,
            conversion_rate=conversion_rate
        )
    
    def classify_call_outcome(self, transcript: str, negotiation_successful: bool, 
                            carrier_verified: bool, loads_available: bool) -> CallOutcome:
        """
        Classify call outcome based on call details
        
        Args:
            transcript: Call transcript
            negotiation_successful: Whether negotiation reached agreement
            carrier_verified: Whether carrier was verified
            loads_available: Whether suitable loads were found
            
        Returns:
            CallOutcome: Classified outcome
        """
        # Simple rule-based classification
        # In production, this could use NLP/ML for better accuracy
        
        if not carrier_verified:
            return CallOutcome.FAILED_VERIFICATION
        
        if not loads_available:
            return CallOutcome.NO_SUITABLE_LOADS
        
        if negotiation_successful:
            return CallOutcome.SUCCESSFUL_BOOKING
        
        # Check transcript for specific indicators
        if transcript:
            transcript_lower = transcript.lower()
            if any(phrase in transcript_lower for phrase in ["not interested", "declined", "pass"]):
                return CallOutcome.REJECTED_BY_CARRIER
            if "transfer" in transcript_lower or "sales rep" in transcript_lower:
                return CallOutcome.TRANSFERRED_TO_SALES
            if any(phrase in transcript_lower for phrase in ["dropped", "hung up", "disconnected"]):
                return CallOutcome.CALL_DROPPED
        
        return CallOutcome.NEGOTIATION_FAILED
    
    def classify_call_sentiment(self, transcript: str) -> CallSentiment:
        """
        Classify call sentiment based on transcript
        
        Args:
            transcript: Call transcript
            
        Returns:
            CallSentiment: Classified sentiment
        """
        if not transcript:
            return CallSentiment.NEUTRAL
        
        transcript_lower = transcript.lower()
        
        # Positive indicators
        positive_words = ["great", "excellent", "perfect", "thank you", "appreciate", "good"]
        positive_count = sum(1 for word in positive_words if word in transcript_lower)
        
        # Negative indicators  
        negative_words = ["frustrated", "angry", "terrible", "awful", "ridiculous", "waste"]
        negative_count = sum(1 for word in negative_words if word in transcript_lower)
        
        # Frustrated indicators
        frustrated_words = ["why", "always", "never", "impossible", "difficult"]
        frustrated_count = sum(1 for word in frustrated_words if word in transcript_lower)
        
        if negative_count > positive_count:
            return CallSentiment.NEGATIVE
        elif frustrated_count > 2:
            return CallSentiment.FRUSTRATED
        elif positive_count > 0:
            return CallSentiment.POSITIVE
        else:
            return CallSentiment.NEUTRAL
    
    async def process_happyrobot_webhook(self, webhook_payload: Dict[str, Any]) -> Optional[Call]:
        """
        Process incoming HappyRobot webhook data and store call information
        
        Args:
            webhook_payload: Full webhook payload from HappyRobot
            
        Returns:
            Call: Created or updated call record
        """
        try:
            # Extract call data and extracted fields from webhook
            call_data = webhook_payload.get("call_data", {})
            
            # Handle extracted_data - could be inside call_data as string or direct object
            extracted_data = {}
            if "extracted_data" in call_data:
                # If it's a string, try to parse as JSON
                raw_extracted = call_data.get("extracted_data")
                if isinstance(raw_extracted, str):
                    try:
                        import json
                        extracted_data = json.loads(raw_extracted)
                    except:
                        logger.warning("Could not parse extracted_data as JSON", raw_data=raw_extracted)
                        extracted_data = {}
                else:
                    extracted_data = raw_extracted or {}
            else:
                # Fallback to top-level extracted_data
                extracted_data = webhook_payload.get("extracted_data", {})
            
            # Generate call ID from HappyRobot call ID or use timestamp
            happyrobot_call_id = call_data.get("happyrobot_call_id", "")
            call_id = f"hr_{happyrobot_call_id}" if happyrobot_call_id else f"call_{int(datetime.utcnow().timestamp())}"
            
            # Map extracted data to call fields
            carrier_mc = extracted_data.get("carrier_mc_number")
            company_name = extracted_data.get("carrier_company_name")
            outcome_str = extracted_data.get("call_outcome", "unknown")
            sentiment_str = extracted_data.get("carrier_sentiment", "neutral")
            
            # Convert strings to enums
            try:
                outcome = CallOutcome(outcome_str.lower()) if outcome_str else CallOutcome.UNKNOWN
            except ValueError:
                outcome = CallOutcome.UNKNOWN
                
            try:
                sentiment = CallSentiment(sentiment_str.lower()) if sentiment_str else CallSentiment.NEUTRAL
            except ValueError:
                sentiment = CallSentiment.NEUTRAL
            
            # Get timing information
            start_time = datetime.utcnow()  # Default to now if not provided
            if call_data.get("start_time"):
                try:
                    start_time = datetime.fromisoformat(call_data["start_time"].replace("Z", "+00:00"))
                except:
                    pass
            
            end_time = datetime.utcnow()
            if call_data.get("end_time"):
                try:
                    end_time = datetime.fromisoformat(call_data["end_time"].replace("Z", "+00:00"))
                except:
                    pass
            
            # Calculate duration
            duration_seconds = int((end_time - start_time).total_seconds())
            
            # Get final rate if available
            final_rate = None
            if extracted_data.get("final_agreed_rate"):
                try:
                    final_rate = float(extracted_data["final_agreed_rate"])
                except (ValueError, TypeError):
                    pass
            
            # Create basic call record
            call_create = CallCreate(
                call_id=call_id,
                carrier_mc_number=carrier_mc,
                start_time=start_time,
                happyrobot_call_id=happyrobot_call_id
            )
            
            # Store the basic call
            call_record = self.create_call(call_create)
            
            # Update with extracted data
            from app.models.call import CallUpdate
            call_update = CallUpdate(
                end_time=end_time,
                duration_seconds=duration_seconds,
                outcome=outcome,
                sentiment=sentiment,
                discussed_load_id=extracted_data.get("discussed_load_id"),
                final_negotiated_rate=final_rate,
                transcript=call_data.get("transcript", ""),
                extracted_data=extracted_data
            )
            
            # Update the call with extracted data
            call_record = self.update_call(call_id, call_update)
            
            logger.info("Successfully processed HappyRobot webhook", 
                       call_id=call_id, 
                       carrier_mc=carrier_mc,
                       outcome=outcome.value if outcome else "unknown")
            
            return call_record
            
        except Exception as e:
            logger.error("Error processing HappyRobot webhook", 
                        error=str(e), 
                        error_type=type(e).__name__,
                        payload=webhook_payload,
                        extracted_data=extracted_data if 'extracted_data' in locals() else "not_extracted")
            # Don't raise the exception, just log it and return None
            return None