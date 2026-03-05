# KhetiPulse AI Backend - Setup & Deployment Guide

This document explains how to set up the AWS infrastructure and run the KhetiPulse backend.

## 🌍 Multilingual Support
KhetiPulse supports: **English (en), Hindi (hi), Telugu (te), Tamil (ta), and Bengali (bn)**.
Users can set their preferred language via the `/preferences/language` endpoint. All subsequent AI responses and data recommendations will be tailored to this language.

---

## 🏗️ AWS Side Setup (Step-by-Step)

### 1. Amazon Bedrock Configuration
- **Enable Models**: Go to Bedrock Console > Model Access. Request access for **Claude 3 Haiku** and **Titan Text Embeddings v2**.
- **Knowledge Base (RAG)**:
  1. Upload your agricultural PDF/DOCX advisories to an S3 bucket (e.g., `s3://khetipulse-docs/`).
  2. Bedrock Console > Knowledge Bases > Create.
  3. Select **Titan Text Embeddings v2** and **OpenSearch Serverless** (managed) as the vector store.
  4. Note the `Knowledge Base ID` and add it to your `.env` or `template.yaml`.

### 2. S3 Bucket (Mandi Data)
- The SAM template creates a bucket named `khetipulse-data-<id>-<region>`.
- Upload a CSV file named `agmarknet_latest.csv` with the following columns: `state, district, market, commodity, variety, arrival_date, min_price, max_price, modal_price`.

### 3. DynamoDB Tables
The SAM template automatically creates:
- `Users`: Stores user profiles and language preferences (PK: `user_id`).
- `AdvisoryHistory`: Stores past LLM recommendations (PK: `user_id`, SK: `timestamp`).

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.11+
- AWS CLI (configured via `aws configure`)

### Setup Steps
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**: Create a `.env` file:
   ```env
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   BEDROCK_KB_ID=your-knowledge-base-id
   OPENWEATHER_API_KEY=your-api-key
   DYNAMODB_TABLE_USERS=Users
   ```
3. **Run FastAPI**:
   ```bash
   uvicorn app.main:app --reload
   ```

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
