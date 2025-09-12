"""
HappyRobot platform integration service
"""
import json
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.security import create_api_key_header


class HappyRobotService:
    """Service for integrating with the HappyRobot platform"""
    
    def __init__(self):
        self.base_url = "https://platform.happyrobot.ai/api/v1" 
        self.api_key = settings.happyrobot_api_key
        self.agent_id = settings.happyrobot_agent_id
        self.org_id = settings.happyrobot_org_id
        self.workflow_id = settings.happyrobot_workflow_id
    
    async def create_inbound_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an inbound agent on the HappyRobot platform
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            Dict[str, Any]: Created agent details
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{self.base_url}/agents",
                headers=headers,
                json=agent_config,
                timeout=30.0
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise Exception(f"Failed to create agent: {response.status_code} - {response.text}")
    
    async def configure_call_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure the call workflow for the inbound agent
        
        Args:
            workflow_config: Workflow configuration
            
        Returns:
            Dict[str, Any]: Workflow configuration result
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{self.base_url}/workflows",
                headers=headers,
                json=workflow_config,
                timeout=30.0
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise Exception(f"Failed to configure workflow: {response.status_code} - {response.text}")
    
    def get_agent_prompt(self) -> str:
        """
        Get the AI agent prompt for carrier calls
        
        Returns:
            str: Agent prompt template
        """
        return """
        You are a professional freight broker assistant handling inbound calls from truck drivers and carriers looking for loads.

        Your primary objectives are:
        1. Greet the caller professionally and get their MC (Motor Carrier) number
        2. Verify their eligibility using the FMCSA database
        3. Understand their equipment type, location, and preferences
        4. Search for and present matching available loads
        5. Negotiate pricing (up to 3 rounds of back-and-forth)
        6. If agreement is reached, transfer to a human sales representative
        7. If no agreement, politely end the call

        Key Guidelines:
        - Always be professional, helpful, and courteous
        - Ask for MC number early in the call for verification
        - Present load details clearly: origin, destination, pickup date, equipment type, rate
        - Be flexible in negotiation but protect company margins
        - Extract key information: carrier details, load preferences, sentiment
        - Classify the call outcome and carrier sentiment at the end

        Available Functions:
        - verify_mc_number(mc_number): Verify carrier with FMCSA
        - search_loads(criteria): Find matching loads
        - evaluate_offer(negotiation_id, carrier_offer): Get negotiation decision
        - transfer_to_sales(): Transfer call to human representative

        Remember: You represent a professional freight brokerage. Maintain high standards of service while protecting business interests.
        """
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """
        Get the complete workflow configuration for the HappyRobot agent
        
        Returns:
            Dict[str, Any]: Workflow configuration
        """
        return {
            "name": "Inbound Carrier Sales Agent",
            "description": "AI agent for handling inbound carrier calls and load booking",
            "type": "inbound",
            "prompt": self.get_agent_prompt(),
            "webhook_url": f"{settings.webhook_url}/webhook/happyrobot" if settings.webhook_url else None,
            "functions": [
                {
                    "name": "verify_mc_number",
                    "description": "Verify carrier MC number with FMCSA",
                    "endpoint": f"{settings.webhook_url}/api/v1/carriers/{'{mc_number}'}/verify-and-update",
                    "method": "POST",
                    "headers": create_api_key_header()
                },
                {
                    "name": "search_loads",
                    "description": "Search for available loads matching carrier criteria",
                    "endpoint": f"{settings.webhook_url}/api/v1/loads/search",
                    "method": "POST",
                    "headers": create_api_key_header()
                },
                {
                    "name": "evaluate_offer",
                    "description": "Evaluate carrier's counter offer",
                    "endpoint": f"{settings.webhook_url}/api/v1/negotiations/{'{negotiation_id}'}/evaluate",
                    "method": "POST",
                    "headers": create_api_key_header()
                },
                {
                    "name": "create_call_record",
                    "description": "Create call record for tracking",
                    "endpoint": f"{settings.webhook_url}/api/v1/calls/",
                    "method": "POST", 
                    "headers": create_api_key_header()
                },
                {
                    "name": "start_negotiation",
                    "description": "Start price negotiation for a load",
                    "endpoint": f"{settings.webhook_url}/api/v1/negotiations/",
                    "method": "POST",
                    "headers": create_api_key_header()
                }
            ],
            "settings": {
                "max_call_duration": 600,  # 10 minutes
                "enable_recording": True,
                "enable_transcription": True,
                "language": "en-US",
                "voice": "professional_male",
                "interruption_sensitivity": "medium"
            }
        }
    
    async def trigger_web_call(self, phone_number: str = None) -> Dict[str, Any]:
        """
        Trigger a web call using existing workflow
        
        Args:
            phone_number: Optional phone number (not used for web calls)
            
        Returns:
            Dict[str, Any]: Call trigger response
        """
        if not self.workflow_id:
            raise Exception("Workflow ID not configured. Please set HAPPYROBOT_WORKFLOW_ID in environment.")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Use HappyRobot webhook trigger endpoint based on documentation
            webhook_endpoint = f"https://workflows.platform.happyrobot.ai/hooks/{self.workflow_id}"
            
            # Web call trigger payload - can include phone number or other data
            call_config = {
                "trigger_type": "web_call",
                "organization_id": self.org_id,
                "phone_number": phone_number if phone_number else "+15551234567"  # Demo number
            }
            
            try:
                response = await client.post(
                    webhook_endpoint,
                    headers=headers,
                    json=call_config,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json() if response.content else {"status": "success"}
                    return {
                        "endpoint_used": webhook_endpoint,
                        "response": result,
                        "use_case_id": self.workflow_id,
                        "organization_id": self.org_id,
                        "status": "triggered"
                    }
                else:
                    return {
                        "endpoint_used": webhook_endpoint,
                        "error": f"API returned status {response.status_code}",
                        "response": response.text
                    }
                        
            except Exception as e:
                return {
                    "endpoint_used": webhook_endpoint,
                    "error": f"Request failed: {str(e)}"
                }
    
    async def get_call_transcript(self, call_id: str) -> Optional[str]:
        """
        Get call transcript from HappyRobot
        
        Args:
            call_id: HappyRobot call ID
            
        Returns:
            str: Call transcript or None if not available
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{self.base_url}/calls/{call_id}/transcript",
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("transcript")
            else:
                return None