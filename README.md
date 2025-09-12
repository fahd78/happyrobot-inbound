# HappyRobot Inbound Carrier Sales Automation

An AI-powered freight brokerage automation system that handles inbound carrier calls for load booking, using the HappyRobot platform for intelligent call management.

## 🎯 Project Overview

This system automates the entire carrier-broker interaction flow:
- **Carrier Authentication**: Verify MC numbers via FMCSA API
- **Load Matching**: Intelligent matching of carriers to available loads
- **Price Negotiation**: Automated negotiation handling (up to 3 rounds)
- **Call Classification**: Sentiment analysis and outcome tracking
- **Metrics Dashboard**: Real-time analytics and reporting

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HappyRobot    │    │   FastAPI       │    │   Database      │
│   AI Agent      │◄───┤   Backend       │◄───┤   (SQLite/PG)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FMCSA API     │    │   Load Matching │    │   Metrics       │
│   Verification  │    │   Engine        │    │   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (for containerization)
- HappyRobot account and API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fahd78/happyrobot-inbound-carrier.git
   cd happyrobot-inbound-carrier
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📊 Features

### Core Functionality
- ✅ **Carrier Verification** - FMCSA MC number validation
- ✅ **Load Management** - CRUD operations for freight loads
- ✅ **Intelligent Matching** - Algorithm-based load-carrier matching
- ✅ **Price Negotiation** - Multi-round automated negotiation
- ✅ **Call Analytics** - Sentiment and outcome classification

### Security
- 🔒 **HTTPS Encryption** - SSL/TLS for all communications
- 🔑 **API Key Authentication** - Secure endpoint access
- 🛡️ **Input Validation** - Comprehensive data sanitization

### Monitoring
- 📈 **Real-time Dashboard** - Live metrics and KPIs
- 📋 **Call Transcripts** - Complete interaction logs
- 🎯 **Performance Analytics** - Success rates and trends

## 🛠️ Development

### Project Structure
```
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   └── main.py           # FastAPI application
├── dashboard/            # Frontend dashboard
├── scripts/              # Utility scripts
├── tests/                # Test suite
└── docker/               # Docker configuration
```

### Running Tests
```bash
pytest tests/ -v
```

### Docker Deployment
```bash
docker build -t happyrobot-carrier .
docker run -p 8000:8000 happyrobot-carrier
```

## 📧 Deliverables

1. **Production System** - Fully functional automation platform
2. **Cloud Deployment** - Live system on cloud infrastructure  
3. **Documentation** - Complete technical and user documentation
4. **Demo Video** - 5-minute walkthrough demonstration
5. **Client Presentation** - Ready for stakeholder review

## 🔗 Links

- **Repository**: [GitHub](https://github.com/fahd78/happyrobot-inbound-carrier)
- **Live Demo**: [Deployment URL]
- **Documentation**: [API Docs]
- **Dashboard**: [Analytics Dashboard]

## 📞 Contact

For technical questions or project inquiries, reach out through the GitHub repository issues.

---
*Built for HappyRobot Stage 2 Technical Challenge*