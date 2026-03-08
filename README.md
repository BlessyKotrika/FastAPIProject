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

---

## 🏗️ Backend Setup (Summary)
1. **Amazon Bedrock**: Enable Claude 3 Haiku and Titan Text Embeddings.
2. **Knowledge Base**: Create and sync with agricultural documentation.
3. **Local Run**: `uvicorn app.main:app --reload`.

## 💻 Frontend Setup (Summary)
1. **Framework**: Next.js 14.
2. **Local Run**: `cd khetipulse-web && npm install && npm run dev`.

---

## ☁️ Deployment Options

### Option 1: AWS ECS with Load Balancer (Recommended)
**Features:**
- Auto-scaling ECS Fargate tasks
- Application Load Balancer for high availability
- GitHub Actions CI/CD pipeline
- Production-ready infrastructure

**Quick Deploy:**
```bash
# 1. Set up AWS infrastructure
./setup-aws-infrastructure.sh

# 2. Configure API keys in SSM Parameter Store
# 3. Push to GitHub main branch for automatic deployment
```

### Option 2: AWS Lambda (Legacy)
**For serverless deployment:**
```bash
sam build
sam deploy --guided
```

---

## 🧪 Testing the Multilingual APIs

### 1. Set Language Preference
```bash
curl -X POST "http://localhost:8000/preferences/language" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "farmer123", "language": "hi"}'
```

### 2. Get Today's Action Cards (Hindi)
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
