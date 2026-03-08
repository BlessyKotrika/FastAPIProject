# KhetiPulse - AI-Powered Farmer Decision Support System

KhetiPulse is a comprehensive, multilingual platform designed to assist Indian farmers with real-time weather-based advice, market insights, and AI-powered agricultural consulting.

## 📚 Project Documentation & Guides

For in-depth information on the project, please refer to the following guides:

*   **[PRESENTATION_FLOW.md](./PRESENTATION_FLOW.md)**: 📽️ **Slide-by-slide presentation flow and script.**
*   **[PRESENTATION_GUIDE.md](./PRESENTATION_GUIDE.md)**: 🎯 **Final Presentation Content, Purpose, and Features.**
*   **[LOCAL_SETUP_GUIDE.md](./LOCAL_SETUP_GUIDE.md)**: 💻 Local development and execution.
*   **[AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)**: ☁️ Production deployment on AWS ECS.
*   **[AWS_CONFIGURATION_GUIDE.md](./AWS_CONFIGURATION_GUIDE.md)**: ⚙️ Configuring AWS services and environment variables.
*   **[FULL_RUN_GUIDE.md](./FULL_RUN_GUIDE.md)**: 🚀 Comprehensive end-to-step execution guide.
*   **[openapi.json](./openapi.json)**: 📖 Latest OpenAPI specification for the backend.

## 🌍 Multilingual & AI Features
KhetiPulse supports: **English (en), Hindi (hi), Telugu (te), Tamil (ta), and Bengali (bn)**.

**Core Capabilities:**
- **AI Advisor (RAG)**: Contextual farming advice using AWS Bedrock Claude 3 Haiku and Knowledge Bases.
- **Smart Mandi**: Real-time market prices from Agmarknet API with a multi-level fallback mechanism (District+State → State → District → Crop) and trend analysis.
- **Onboarding API**: Centralized state, district, and crop metadata for improved resilience.
- **Weather Actions**: Hyper-local weather forecast (OpenWeather API) and recommended farm actions.
- **Local & Google Auth**: Secure user accounts with JWT-based local login or Google OAuth2.

---

## 🏗️ Backend Setup (Summary)
1. **Amazon Bedrock**: Enable Claude 3 Haiku and Titan Text Embeddings v2.
2. **Knowledge Base**: Create and sync with agricultural documentation (optional for basic LLM mode).
3. **Environment**: Create `.env` based on `.env.example`.
4. **Local Run**: `uvicorn app.main:app --reload`.

## 💻 Frontend Setup (Summary)
1. **Framework**: Next.js 14.
2. **Local Run**: `cd khetipulse-web && npm install && npm run dev`.

---

## 📖 API Documentation & OpenAPI Spec
KhetiPulse provides comprehensive API documentation:
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Specification**: The latest `openapi.json` is available in the project root.

To regenerate the OpenAPI spec file after code changes:
```bash
python3 -c 'import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))' > openapi.json
```

---

## ☁️ Deployment Options

### Option 1: AWS ECS with Load Balancer (Recommended)
**Features:**
- Auto-scaling ECS Fargate tasks with Application Load Balancer
- Infrastructure as Code (CloudFormation)
- GitHub Actions CI/CD for automated build/deploy
- Secure parameter management via AWS SSM Secrets Manager

**Quick Deploy:**
```bash
# 1. Provision Infrastructure (ECR, DynamoDB, VPC, ECS, ALB)
./setup-aws-infrastructure.sh

# 2. Configure Secrets in SSM (OpenWeather, Bedrock, etc.)
# 3. Push to 'main' branch for GitHub Actions deployment
```

### Option 2: AWS Lambda (Legacy)
**For serverless deployment:**
```bash
sam build
sam deploy --guided
```

---

## 🧪 Testing the APIs

### 1. Onboarding (Metadata)
```bash
# Get all supported states
curl -X GET "http://localhost:8000/onboarding/states"

# Get districts for a specific state
curl -X GET "http://localhost:8000/onboarding/districts/Uttar%20Pradesh"

# Get all supported crops
curl -X GET "http://localhost:8000/onboarding/crops"
```

### 2. Set Language Preference
```bash
curl -X POST "http://localhost:8000/preferences/language" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "farmer123", "language": "hi"}'
```

### 3. Get Today's Action Cards (Hindi)
```bash
curl -X POST "http://localhost:8000/today" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "farmer123",
       "crop": "wheat",
       "location": "Barabanki",
       "sowing_date": "2025-11-01",
       "language": "hi"
     }'
```

### 3. Sell Smart (Mandi Recommendation)
```bash
curl -X POST "http://localhost:8000/sell-smart" \
     -H "Content-Type: application/json" \
     -d '{"crop": "Wheat", "location": "Barabanki", "language": "te"}'
```

### 4. RAG Chat (Telugu)
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "వరి పంటకు ఏ ఎరువులు వాడాలి?",
       "language": "te",
       "crop": "paddy"
     }'
```
