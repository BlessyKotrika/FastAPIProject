# KhetiPulse - AI-Powered Farmer Decision Support System

KhetiPulse is a comprehensive, multilingual platform designed to assist Indian farmers with real-time weather-based advice, market insights, and AI-powered agricultural consulting.

## 🚀 Quick Start Guide

**For full setup and running instructions, please refer to:**
👉 **[LOCAL_SETUP_GUIDE.md](./LOCAL_SETUP_GUIDE.md)**

For AWS Cloud Deployment (SAM/Lambda):
👉 **[FULL_RUN_GUIDE.md](./FULL_RUN_GUIDE.md)**

---

## 🌍 Multilingual Support
KhetiPulse supports: **English (en), Hindi (hi), Telugu (te), Tamil (ta), and Bengali (bn)**.
Users can set their preferred language via the onboarding wizard or the `/preferences/language` endpoint.

---

## 🏗️ Backend Setup (Summary)
1. **Amazon Bedrock**: Enable Claude 3 Haiku and Titan Text Embeddings.
2. **Knowledge Base**: Create and sync with agricultural documentation.
3. **Local Run**: `uvicorn app.main:app --reload`.

## 💻 Frontend Setup (Summary)
1. **Framework**: Next.js 14.
2. **Local Run**: `cd khetipulse-web && npm install && npm run dev`.

---

## ☁️ Deployment to AWS (Lambda)

1. **Build**:
   ```bash
   sam build
   ```
2. **Deploy**:
   ```bash
   sam deploy --guided
   ```
   Follow the prompts to set the stack name and region. Note the `ApiUrl` in the outputs.

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
