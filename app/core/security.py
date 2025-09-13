from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings


security = HTTPBearer()


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
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
    return {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json"
    }