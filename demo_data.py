#!/usr/bin/env python3
"""
Demo script to populate the dashboard with sample call data
This shows how the system works when real calls are made
"""

import requests
import json
from datetime import datetime, timedelta
import random

# API Configuration
BASE_URL = "http://127.0.0.1:8001"
API_KEY = "dev-api-key-change-in-production"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_sample_calls():
    """Create sample call records to demonstrate the dashboard"""
    
    sample_calls = [
        {
            "call_id": "DEMO_001",
            "carrier_mc_number": "123456",
            "happyrobot_call_id": "hr_demo_001",
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=2) + timedelta(minutes=8)).isoformat(),
            "duration_seconds": 480,
            "outcome": "successful_booking",
            "sentiment": "positive",
            "discussed_load_id": "LD001",
            "final_rate": 1450.00,
            "transcript": "Carrier called looking for loads. Verified MC 123456, offered LA to Phoenix load, negotiated from $1500 to $1450."
        },
        {
            "call_id": "DEMO_002", 
            "carrier_mc_number": "789012",
            "happyrobot_call_id": "hr_demo_002",
            "start_time": (datetime.now() - timedelta(hours=4)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=4) + timedelta(minutes=12)).isoformat(),
            "duration_seconds": 720,
            "outcome": "rejected_by_carrier",
            "sentiment": "neutral",
            "discussed_load_id": "LD002",
            "transcript": "Carrier called for reefer loads. Offered Dallas to Atlanta for $2200, but carrier declined due to temperature requirements."
        },
        {
            "call_id": "DEMO_003",
            "carrier_mc_number": "456789",
            "happyrobot_call_id": "hr_demo_003", 
            "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=1) + timedelta(minutes=15)).isoformat(),
            "duration_seconds": 900,
            "outcome": "negotiation_failed",
            "sentiment": "frustrated",
            "discussed_load_id": "LD003",
            "transcript": "Carrier wanted $2000 for Chicago to Denver flatbed load, but our max was $1800. Could not reach agreement after 3 rounds."
        },
        {
            "call_id": "DEMO_004",
            "carrier_mc_number": "123456",
            "happyrobot_call_id": "hr_demo_004",
            "start_time": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "end_time": (datetime.now() - timedelta(minutes=30) + timedelta(minutes=6)).isoformat(),
            "duration_seconds": 360,
            "outcome": "no_suitable_loads",
            "sentiment": "neutral",
            "transcript": "Carrier looking for oversized loads but none available in their area."
        }
    ]
    
    print("Creating sample call records...")
    for call in sample_calls:
        try:
            response = requests.post(f"{BASE_URL}/api/v1/calls/", 
                                   headers=headers, 
                                   json=call)
            if response.status_code in [200, 201]:
                print(f"[OK] Created call: {call['call_id']}")
            else:
                print(f"[ERROR] Failed to create call {call['call_id']}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Error creating call {call['call_id']}: {e}")

def create_sample_negotiations():
    """Create sample negotiations"""
    
    negotiations = [
        {
            "negotiation_id": "NEG_001",
            "call_id": "DEMO_001",
            "load_id": "LD001",
            "carrier_mc_number": "123456",
            "original_rate": 1500.00,
            "current_offer_amount": 1450.00,
            "final_agreed_rate": 1450.00,
            "status": "accepted",
            "current_round": 2,
            "max_rounds": 3
        }
    ]
    
    print("Creating sample negotiations...")
    for neg in negotiations:
        try:
            response = requests.post(f"{BASE_URL}/api/v1/negotiations/", 
                                   headers=headers, 
                                   json=neg)
            if response.status_code in [200, 201]:
                print(f"[OK] Created negotiation: {neg['negotiation_id']}")
            else:
                print(f"[ERROR] Failed to create negotiation: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Error creating negotiation: {e}")

if __name__ == "__main__":
    print("Creating Demo Data for HappyRobot Dashboard")
    print("=" * 50)
    
    # Wait a moment for API to be ready
    import time
    time.sleep(2)
    
    try:
        # Test API connectivity
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("[OK] API is accessible")
        else:
            print(f"[WARN] API responded with status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to API: {e}")
        print("Make sure the FastAPI server is running on port 8001")
        exit(1)
    
    create_sample_calls()
    create_sample_negotiations()
    
    print("\nDemo data created successfully!")
    print("\nView the dashboard at: http://localhost:8001/dashboard")
    print("View API docs at: http://localhost:8001/docs")
    print("\nThe dashboard should now show:")
    print("- Total Calls: 4")
    print("- Successful Bookings: 1") 
    print("- Various outcomes and sentiments")
    print("- Recent calls table populated")