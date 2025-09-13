import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    
    app_name: str = "HappyRobot Inbound Carrier Sales"
    environment: str = "development"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    database_url: str = "sqlite:///./happyrobot.db"
    
    api_key: str = "dev-api-key-change-in-production"
    secret_key: str = "dev-secret-key-change-in-production"
    
    happyrobot_api_key: Optional[str] = None
    happyrobot_base_url: str = "https://api.happyrobot.ai"
    happyrobot_agent_id: Optional[str] = None
    happyrobot_org_id: Optional[str] = None
    happyrobot_workflow_id: Optional[str] = None
    happyrobot_phone_number: Optional[str] = None
    
    fmcsa_api_key: Optional[str] = None
    fmcsa_base_url: str = "https://mobile.fmcsa.dot.gov"
    
    webhook_url: Optional[str] = None
    
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


settings = Settings()