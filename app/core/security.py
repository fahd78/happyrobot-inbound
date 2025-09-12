"""
Security utilities for API authentication and authorization
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings


# HTTP Bearer token security scheme
security = HTTPBearer()


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify API key from Authorization header
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        bool: True if valid API key
        
    Raises:
        HTTPException: If invalid or missing API key
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True


def create_api_key_header():
    """
    Create API key header for external requests
    
    Returns:
        dict: Authorization header with API key
    """
    return {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json"
    }