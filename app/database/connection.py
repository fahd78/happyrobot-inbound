"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
from app.models.load import Base
from app.models.carrier import Carrier
from app.models.call import Call
from app.models.negotiation import Negotiation

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_database():
    """
    Get database session dependency for FastAPI
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database with sample data"""
    create_tables()
    
    # Add sample loads for testing
    from app.services.load_service import LoadService
    from app.models.load import LoadCreate
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    db = SessionLocal()
    load_service = LoadService(db)
    
    # Sample loads data
    sample_loads = [
        LoadCreate(
            load_id="LD001",
            origin="Los Angeles, CA",
            destination="Phoenix, AZ",
            pickup_datetime=datetime.now() + timedelta(days=2),
            delivery_datetime=datetime.now() + timedelta(days=3),
            equipment_type="Dry Van",
            loadboard_rate=Decimal("1500.00"),
            notes="Standard dry freight, no hazmat",
            weight=25000,
            commodity_type="General Freight",
            num_of_pieces=1,
            miles=370,
            dimensions="48x53x102"
        ),
        LoadCreate(
            load_id="LD002", 
            origin="Dallas, TX",
            destination="Atlanta, GA",
            pickup_datetime=datetime.now() + timedelta(days=1),
            delivery_datetime=datetime.now() + timedelta(days=4),
            equipment_type="Reefer",
            loadboard_rate=Decimal("2200.00"),
            notes="Temperature controlled, -10°F",
            weight=40000,
            commodity_type="Frozen Food",
            num_of_pieces=24,
            miles=925,
            dimensions="48x53x102"
        ),
        LoadCreate(
            load_id="LD003",
            origin="Chicago, IL", 
            destination="Denver, CO",
            pickup_datetime=datetime.now() + timedelta(days=3),
            delivery_datetime=datetime.now() + timedelta(days=5),
            equipment_type="Flatbed",
            loadboard_rate=Decimal("1800.00"),
            notes="Steel beams, tarps required",
            weight=45000,
            commodity_type="Steel",
            num_of_pieces=10,
            miles=920,
            dimensions="48x8.5x8.5"
        )
    ]
    
    try:
        for load_data in sample_loads:
            existing = load_service.get_load(load_data.load_id)
            if not existing:
                load_service.create_load(load_data)
        
        print("Database initialized with sample data")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
    finally:
        db.close()