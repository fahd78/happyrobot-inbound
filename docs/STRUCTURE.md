# HappyRobot Inbound Carrier Sales - Repository Structure

## 📁 Directory Organization

```
happyrobot-inbound-carrier/
│
├── 📄 Root Files
│   ├── README.md                 # Main project documentation
│   ├── QUICKSTART.md            # Quick setup guide
│   ├── STRUCTURE.md             # This file - repository structure
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment variables template
│   ├── .gitignore              # Git ignore rules
│   └── setup.bat               # Windows setup script
│
├── 📂 app/                     # Core Application
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── 📂 api/                 # REST API Endpoints
│   │   ├── __init__.py
│   │   ├── loads.py            # Load management endpoints
│   │   ├── carriers.py         # Carrier management endpoints
│   │   ├── calls.py            # Call tracking endpoints
│   │   └── negotiations.py     # Negotiation endpoints
│   │
│   ├── 📂 core/                # Core Configuration
│   │   ├── config.py           # Application settings
│   │   └── security.py         # Authentication & security
│   │
│   ├── 📂 database/            # Database Layer
│   │   ├── __init__.py
│   │   └── connection.py       # Database connection & setup
│   │
│   ├── 📂 models/              # Data Models
│   │   ├── __init__.py
│   │   ├── load.py             # Load data models
│   │   ├── carrier.py          # Carrier data models
│   │   ├── call.py             # Call data models
│   │   └── negotiation.py      # Negotiation data models
│   │
│   └── 📂 services/            # Business Logic
│       ├── __init__.py
│       ├── load_service.py     # Load management service
│       ├── carrier_service.py  # Carrier & FMCSA service
│       ├── call_service.py     # Call tracking service
│       ├── negotiation_service.py # Negotiation logic
│       └── happyrobot_service.py  # HappyRobot integration
│
├── 📂 config/                  # Configuration Files
│   ├── development.env         # Development environment
│   ├── production.env          # Production environment
│   └── requirements_minimal.txt # Minimal dependencies
│
├── 📂 dashboard/               # Analytics Dashboard
│   ├── index.html              # Dashboard HTML
│   └── dashboard.js            # Dashboard JavaScript
│
├── 📂 data/                    # Data Directory
│   └── happyrobot.db           # SQLite database (dev)
│
├── 📂 deployment/              # Deployment Configuration
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── Dockerfile              # Docker container definition
│   ├── .dockerignore           # Docker ignore rules
│   ├── fly.toml                # Fly.io deployment config
│   └── railway.json            # Railway deployment config
│
├── 📂 docs/                    # Documentation
│   ├── CLIENT_EMAIL.md         # Client email template
│   ├── CLIENT_PROPOSAL.md      # Technical proposal
│   ├── DEMO_VIDEO_SCRIPT.md    # Demo video script
│   └── FDE Technical Challenge - Inbound Carrier Sales (1).pdf
│
├── 📂 examples/                # Usage Examples
│   ├── api_examples.py         # API usage examples
│   └── sample_data.json        # Sample data for testing
│
├── 📂 scripts/                 # Utility Scripts
│   ├── setup.sh                # Linux/Mac setup script
│   ├── deploy.sh               # Deployment script
│   └── init-db.sql             # Database initialization
│
└── 📂 tests/                   # Test Suite
    ├── __init__.py
    ├── conftest.py             # Pytest configuration
    ├── quick_test.py           # Quick setup test
    ├── test_setup.py           # Comprehensive setup test
    │
    ├── 📂 unit/                # Unit Tests
    │   └── (unit test files)
    │
    └── 📂 integration/         # Integration Tests
        └── (integration test files)
```

## 🎯 Key Components

### Core Application (`app/`)
- **main.py**: FastAPI application with all routes and middleware
- **api/**: RESTful API endpoints organized by domain
- **core/**: Application configuration and security
- **models/**: Pydantic and SQLAlchemy data models
- **services/**: Business logic and external integrations
- **database/**: Database connection and initialization

### Configuration (`config/`)
- **development.env**: Local development settings
- **production.env**: Production environment template
- **requirements_minimal.txt**: Minimal dependencies for Windows

### Dashboard (`dashboard/`)
- **index.html**: Real-time analytics dashboard
- **dashboard.js**: Interactive charts and API integration

### Deployment (`deployment/`)
- **Docker files**: Complete containerization setup
- **Cloud configs**: Railway, Fly.io deployment configurations

### Documentation (`docs/`)
- **Technical proposal**: Complete client documentation
- **Email template**: Ready-to-send client communication
- **Demo script**: 5-minute video walkthrough outline

### Examples (`examples/`)
- **API examples**: Python scripts showing API usage
- **Sample data**: JSON examples for loads and carriers

### Scripts (`scripts/`)
- **Setup scripts**: Automated environment setup
- **Deployment**: Cloud deployment automation
- **Database**: Initialization and migration scripts

### Tests (`tests/`)
- **Setup verification**: Quick and comprehensive testing
- **Unit tests**: Individual component testing
- **Integration tests**: End-to-end workflow testing

## 🚀 Quick Navigation

### To Get Started:
1. **Setup**: Run `setup.bat` (Windows) or `./scripts/setup.sh` (Linux/Mac)
2. **Configure**: Copy appropriate config from `config/` to `.env`
3. **Run**: `python -m uvicorn app.main:app --reload`

### To Deploy:
1. **Local**: `./scripts/deploy.sh local`
2. **Cloud**: `./scripts/deploy.sh [railway|fly]`
3. **Docker**: Use files in `deployment/`

### To Test:
1. **Quick**: `python tests/quick_test.py`
2. **Full**: `python tests/test_setup.py`
3. **API**: `python examples/api_examples.py`

### To Customize:
- **Business Logic**: Modify `app/services/`
- **API Endpoints**: Update `app/api/`
- **Dashboard**: Edit `dashboard/index.html`
- **Configuration**: Update `config/` files

## 📋 File Descriptions

### Root Level Files
- **README.md**: Main project overview and features
- **QUICKSTART.md**: 5-minute setup guide
- **requirements.txt**: All Python package dependencies
- **.env.example**: Environment variables template
- **setup.bat**: Automated Windows setup script

### Important Notes
- **data/**: Contains runtime databases and logs (gitignored)
- **config/**: Environment-specific configurations
- **deployment/**: All containerization and cloud deployment files
- **examples/**: Working code examples for API integration
- **tests/**: Comprehensive testing suite with setup verification

This structure ensures clear separation of concerns, easy maintenance, and professional organization suitable for both development and production deployment.