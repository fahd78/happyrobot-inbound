# HappyRobot Inbound Carrier Sales - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Git (for cloning)
- Internet connection (for API integrations)

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2: Manual Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/fahd78/happyrobot-inbound-carrier.git
   cd happyrobot-inbound-carrier
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

5. **Initialize Database**
   ```bash
   python -c "from app.database.connection import init_database; init_database()"
   ```

6. **Test Setup**
   ```bash
   python test_setup.py
   ```

## ▶️ Running the Application

### Development Mode
```bash
python -m uvicorn app.main:app --reload
```

### Production Mode
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker-compose up -d
```

## 🌐 Access Points

Once running, access these URLs:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Analytics Dashboard**: http://localhost:8000/dashboard
- **Health Check**: http://localhost:8000/health

## 🔑 Required Configuration

Update your `.env` file with:

```env
# HappyRobot Platform
HAPPYROBOT_API_KEY=your-happyrobot-api-key
HAPPYROBOT_BASE_URL=https://api.happyrobot.ai
HAPPYROBOT_AGENT_ID=your-agent-id

# FMCSA API
FMCSA_API_KEY=your-fmcsa-api-key

# Security
API_KEY=your-secure-api-key-here
SECRET_KEY=your-secret-key-for-jwt-signing

# Webhooks
WEBHOOK_URL=https://your-domain.com
```

## 🧪 Testing the System

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Create a Load
```bash
curl -X POST "http://localhost:8000/api/v1/loads/" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "load_id": "TEST001",
    "origin": "Los Angeles, CA",
    "destination": "Phoenix, AZ", 
    "pickup_datetime": "2025-09-10T08:00:00",
    "delivery_datetime": "2025-09-11T17:00:00",
    "equipment_type": "Dry Van",
    "loadboard_rate": 1500.00,
    "commodity_type": "General Freight",
    "weight": 25000,
    "miles": 370
  }'
```

### 3. Verify Carrier
```bash
curl -X POST "http://localhost:8000/api/v1/carriers/123456/verify" \
  -H "Authorization: Bearer your-api-key"
```

### 4. View Dashboard
Open http://localhost:8000/dashboard in your browser

## 🐳 Docker Deployment

### Local Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.yml --profile production up -d
```

## ☁️ Cloud Deployment

### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway up
```

### Fly.io
```bash
# Install Fly CLI (see: https://fly.io/docs/getting-started/installing-flyctl/)
flyctl launch --no-deploy
flyctl deploy
```

### Manual Deployment Script
```bash
./scripts/deploy.sh [local|railway|fly]
```

## 📊 Dashboard Features

The analytics dashboard provides:

- **Real-time Metrics**: Call volume, conversion rates, success rates
- **Visual Analytics**: Pie charts for outcomes, bar charts for sentiment
- **Recent Calls Table**: Live feed of carrier interactions
- **Performance Tracking**: Historical data and trends

## 🔧 API Endpoints

### Loads
- `GET /api/v1/loads/` - List all loads
- `POST /api/v1/loads/` - Create new load
- `GET /api/v1/loads/{load_id}` - Get specific load
- `PUT /api/v1/loads/{load_id}` - Update load
- `POST /api/v1/loads/search` - Search matching loads

### Carriers
- `GET /api/v1/carriers/` - List all carriers
- `POST /api/v1/carriers/` - Create new carrier
- `GET /api/v1/carriers/{mc_number}` - Get specific carrier
- `POST /api/v1/carriers/{mc_number}/verify` - Verify with FMCSA

### Calls
- `GET /api/v1/calls/` - List recent calls
- `POST /api/v1/calls/` - Create call record
- `GET /api/v1/calls/{call_id}` - Get specific call
- `POST /api/v1/calls/{call_id}/classify` - Classify call outcome

### Negotiations
- `POST /api/v1/negotiations/` - Start negotiation
- `POST /api/v1/negotiations/{id}/counter-offer` - Make counter offer
- `POST /api/v1/negotiations/{id}/evaluate` - Evaluate carrier offer

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   - Run: `pip install -r requirements.txt`
   - Check Python version: `python --version` (3.8+ required)

2. **Database Issues**
   - Delete database file: `rm *.db`
   - Reinitialize: `python -c "from app.database.connection import init_database; init_database()"`

3. **Port Already in Use**
   - Change port: `uvicorn app.main:app --port 8001`
   - Kill process: `lsof -ti:8000 | xargs kill -9` (Mac/Linux)

4. **API Key Errors**
   - Check `.env` file exists and has correct API_KEY
   - Verify Authorization header: `Bearer your-api-key`

### Getting Help

- **GitHub Issues**: https://github.com/fahd78/happyrobot-inbound-carrier/issues
- **Documentation**: Check `/docs` folder for detailed guides
- **Logs**: Check `logs/` directory for error details

## 🎯 Next Steps

1. **Configure HappyRobot Agent**: Set up your inbound call agent
2. **Add Real Data**: Import your existing loads and carriers
3. **Customize Business Rules**: Adjust negotiation parameters
4. **Set Up Monitoring**: Configure alerts and notifications
5. **Scale Deployment**: Move to production infrastructure

## 📈 Monitoring & Maintenance

### Health Monitoring
- **Health Endpoint**: `/health` for system status
- **Metrics Endpoint**: `/api/v1/calls/analytics/summary`
- **Dashboard**: Real-time system performance

### Backup & Recovery
- **Database**: Automated backups in production
- **Configuration**: Version control for all settings
- **Data Export**: API endpoints for data extraction

---

**🎉 You're Ready!**

Your HappyRobot Inbound Carrier Sales system is now operational. Start by creating some sample loads and carriers, then trigger test calls to see the full automation in action.

For production deployment, follow the cloud deployment guides and ensure all API keys are properly configured.