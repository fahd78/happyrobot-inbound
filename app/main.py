"""
Main FastAPI application for HappyRobot Inbound Carrier Sales
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import structlog
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.database.connection import init_database
from app.api import loads, carriers, calls, negotiations

# Configure structured logging
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(30 if settings.environment == "production" else 10),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting HappyRobot Inbound Carrier Sales API", environment=settings.environment)
    
    # Initialize database
    init_database()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HappyRobot Inbound Carrier Sales API")


# Create FastAPI application
app = FastAPI(
    title="HappyRobot Inbound Carrier Sales API",
    description="""
    AI-powered freight brokerage automation system that handles inbound carrier calls 
    for load booking, using the HappyRobot platform for intelligent call management.
    
    ## Features
    
    * **Load Management**: CRUD operations for freight loads
    * **Carrier Verification**: FMCSA MC number validation
    * **Call Tracking**: Complete call lifecycle management
    * **Negotiation Engine**: Multi-round automated price negotiation
    * **Analytics**: Call metrics and performance tracking
    
    ## Security
    
    All endpoints require Bearer token authentication via the `Authorization` header.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(loads.router, prefix="/api/v1")
app.include_router(carriers.router, prefix="/api/v1")
app.include_router(calls.router, prefix="/api/v1")
app.include_router(negotiations.router, prefix="/api/v1")

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HappyRobot Inbound Carrier Sales API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs_url": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": "2025-09-07T00:00:00Z"
    }


@app.get("/dashboard")
async def dashboard():
    """Serve the analytics dashboard"""
    dashboard_path = os.path.join("dashboard", "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")


@app.post("/webhook/happyrobot")
async def happyrobot_webhook(request: Request):
    """
    Webhook endpoint for HappyRobot platform integration
    
    This endpoint receives call events from HappyRobot and processes them accordingly.
    """
    try:
        # Get the webhook payload
        payload = await request.json()
        
        # Log the webhook event
        logger.info("Received HappyRobot webhook", payload=payload)
        
        # Process different event types
        event_type = payload.get("event_type")
        call_data = payload.get("call_data", {})
        
        if event_type == "call_started":
            # Handle call start
            logger.info("Processing call started event", call_id=call_data.get("call_id"))
            
        elif event_type == "call_ended":
            # Handle call end
            logger.info("Processing call ended event", call_id=call_data.get("call_id"))
            
        elif event_type == "call_transcript":
            # Handle transcript received
            logger.info("Processing transcript event", call_id=call_data.get("call_id"))
            
        else:
            logger.warning("Unknown webhook event type", event_type=event_type)
        
        return {"status": "received", "event_type": event_type}
        
    except Exception as e:
        logger.error("Error processing webhook", error=str(e))
        raise HTTPException(status_code=400, detail="Error processing webhook")


@app.post("/api/v1/test/web-call")
async def trigger_web_call():
    """
    Trigger a test web call using HappyRobot's web call feature
    
    This endpoint will trigger a web call to demonstrate the system functionality
    without needing a phone number.
    """
    try:
        from app.services.happyrobot_service import HappyRobotService
        
        happyrobot_service = HappyRobotService()
        
        # Trigger a web call with your workflow
        result = await happyrobot_service.trigger_web_call()
        
        logger.info("Web call triggered successfully", result=result)
        
        return {
            "status": "success",
            "message": "Web call triggered successfully",
            "call_data": result,
            "instructions": "Check the HappyRobot interface for the web call session"
        }
        
    except Exception as e:
        logger.error("Failed to trigger web call", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to trigger web call: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error("Unhandled exception", 
                path=request.url.path, 
                method=request.method,
                error=str(exc))
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )