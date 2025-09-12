"""
Configuration management for the HappyRobot Inbound Carrier Sales system
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "HappyRobot Inbound Carrier Sales"
    environment: str = "development"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./happyrobot.db"
    
    # Security
    api_key: str = "dev-api-key-change-in-production"
    secret_key: str = "dev-secret-key-change-in-production"
    
    # HappyRobot Platform
    happyrobot_api_key: Optional[str] = None
    happyrobot_base_url: str = "https://api.happyrobot.ai"
    happyrobot_agent_id: Optional[str] = None
    happyrobot_org_id: Optional[str] = None
    happyrobot_workflow_id: Optional[str] = None
    happyrobot_phone_number: Optional[str] = None
    
    # FMCSA API
    fmcsa_api_key: Optional[str] = None
    fmcsa_base_url: str = "https://mobile.fmcsa.dot.gov"
    
    # Webhooks
    webhook_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    @validator("environment")
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()