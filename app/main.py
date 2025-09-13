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
    logger.info("Starting HappyRobot Inbound Carrier Sales API", environment=settings.environment)
    
    init_database()
    logger.info("Database initialized")
    
    yield
    
    logger.info("Shutting down HappyRobot Inbound Carrier Sales API")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loads.router, prefix="/api/v1")
app.include_router(carriers.router, prefix="/api/v1")
app.include_router(calls.router, prefix="/api/v1")
app.include_router(negotiations.router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/")
async def root():
    return {
        "message": "HappyRobot Inbound Carrier Sales API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs_url": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": "2025-09-07T00:00:00Z"
    }


@app.get("/dashboard")
async def dashboard():
    dashboard_path = os.path.join("dashboard", "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")


@app.post("/webhook/happyrobot")
async def happyrobot_webhook(request: Request):
    try:
        payload = await request.json()
        
        logger.info("Received HappyRobot webhook", payload=payload)
        
        event_type = payload.get("event_type")
        call_data = payload.get("call_data", {})
        
        if event_type == "call_started":
            logger.info("Processing call started event", call_id=call_data.get("call_id"))
            
        elif event_type == "call_ended" or event_type == "call_completed":
            logger.info("Processing call completed event", 
                       call_id=call_data.get("happyrobot_call_id"),
                       payload_keys=list(payload.keys()),
                       call_data_keys=list(call_data.keys()))
            
            try:
                from app.services.call_service import CallService
                from app.database.connection import SessionLocal
                
                db = SessionLocal()
                try:
                    call_service = CallService(db)
                    result = await call_service.process_happyrobot_webhook(payload)
                    logger.info("Webhook processing result", success=result is not None)
                finally:
                    db.close()
                    
            except Exception as db_error:
                logger.error("Database processing failed", error=str(db_error))
            
        elif event_type == "call_transcript":
            logger.info("Processing transcript event", call_id=call_data.get("call_id"))
            
        else:
            logger.warning("Unknown webhook event type", event_type=event_type)
        
        return {"status": "received", "event_type": event_type}
        
    except Exception as e:
        logger.error("Error processing webhook", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    payload=payload if 'payload' in locals() else "no_payload")
        return {"status": "error", "message": str(e), "event_type": payload.get("event_type") if 'payload' in locals() else "unknown"}


@app.post("/api/v1/test/webhook")
async def test_webhook_processing():
    try:
        test_payload = {
            "event_type": "call_completed",
            "call_data": {
                "call_id": "test_123",
                "start_time": "2024-12-12T10:00:00Z",
                "end_time": "2024-12-12T10:05:00Z",
                "transcript": "Test call transcript"
            },
            "extracted_data": {
                "carrier_mc_number": "123456",
                "carrier_company_name": "Test Trucking LLC", 
                "equipment_type": "Dry Van",
                "call_outcome": "successful_booking",
                "carrier_sentiment": "positive",
                "final_agreed_rate": "1500.00",
                "discussed_load_id": "TEST001"
            }
        }
        
        from app.services.call_service import CallService
        from app.database.connection import SessionLocal
        
        db = SessionLocal()
        try:
            call_service = CallService(db)
            result = await call_service.process_happyrobot_webhook(test_payload)
        finally:
            db.close()
        
        return {
            "status": "success",
            "message": "Test call data created",
            "call_id": result.call_id if result else "unknown"
        }
        
    except Exception as e:
        logger.error("Test webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@app.post("/api/v1/test/web-call")
async def trigger_web_call():
    try:
        from app.services.happyrobot_service import HappyRobotService
        
        happyrobot_service = HappyRobotService()
        
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