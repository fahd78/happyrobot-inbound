# HappyRobot Inbound Carrier Sales Automation

AI-powered freight brokerage automation system that handles inbound carrier calls using the HappyRobot platform.

## Features

- **AI Call Handling** - Automated carrier interactions with professional greeting, MC verification, and load matching
- **FMCSA Integration** - Real-time carrier verification and compliance checking  
- **Smart Negotiation** - Multi-round price negotiation with up to 3 counter-offers
- **Analytics Dashboard** - Live metrics, call outcomes, and performance tracking
- **Production Ready** - Containerized deployment with HTTPS and authentication

## Quick Start

```bash
git clone https://github.com/fahd78/happyrobot-inbound.git
cd happyrobot-inbound
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -c "from app.database.connection import init_database; init_database()"
python -m uvicorn app.main:app --reload
```

**Access Points:**
- API: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard  
- API Docs: http://localhost:8000/docs

## API Endpoints

**Core Operations:**
- Loads: Create, search, and manage freight loads
- Carriers: FMCSA verification and carrier management  
- Calls: Analytics and call outcome tracking
- Integration: HappyRobot webhook and test endpoints  

## Deployment

**Docker:**
```bash
docker build -t happyrobot-inbound .
docker run -p 8000:8000 happyrobot-inbound
```

**Railway:**
```bash
railway up
```

**Required Environment Variables:**
```env
HAPPYROBOT_API_KEY=your-api-key
HAPPYROBOT_WORKFLOW_ID=your-workflow-id  
FMCSA_API_KEY=your-fmcsa-key
API_KEY=your-auth-key
SECRET_KEY=your-jwt-secret
```

## Repository

https://github.com/fahd78/happyrobot-inbound.git