# KhetiPulse - AI-Powered Multilingual Farmer Decision Support System

KhetiPulse is a production-grade agricultural platform designed to empower farmers with real-time, localized, and actionable insights. By leveraging advanced AI (AWS Bedrock), real-time weather data, and government market (Mandi) APIs, KhetiPulse provides a comprehensive digital assistant for modern farming.

---

## 🚀 Core Features

### 1. **Hyper-Localized Weather & Advisory (Today Actions)**
- **Real-time Forecasts**: Integrates with OpenWeatherMap to provide 48-hour forecasts for the farmer's specific location.
- **Smart Recommendations**: A recommendation engine combines weather data with the current crop stage (e.g., Vegetative, Flowering) to generate "Do Today," "Avoid Today," and "Prepare" action cards.
- **Risk Mitigation**: Automatically warns against spraying pesticides or fertilizers during high winds or forecasted rain.

### 2. **Mandi Insights (Sell Smart)**
- **Live Market Rates**: Connects to the **AGMARKNET (data.gov.in)** API to fetch real-time commodity prices across Indian Mandis.
- **Best Market Discovery**: Algorithms suggest the best market (Mandi) based on the highest price and proximity to the farmer.
- **Trend Analysis**: Provides 7-day price trends and forecasts to help farmers decide whether to sell now or hold for better profits.

### 3. **AI Advisor (Ask KhetiPulse)**
- **RAG-Powered Chat**: Uses Retrieval-Augmented Generation (RAG) with **AWS Bedrock (Claude)** and a specialized agricultural knowledge base to answer complex farming queries.
- **Multilingual Support**: Farmers can ask questions and receive advice in **English, Hindi, Telugu, Tamil, and Bengali**.
- **Context Awareness**: The AI understands the farmer's specific crop, location, and history to provide tailored advice.

### 4. **Government Schemes & Policies**
- **Eligibility Matching**: Automatically filters relevant central and state government schemes (e.g., PM-KISAN, PM-FBY) based on the farmer's state and crop.
- **Application Guidance**: Provides direct links and lists required documents for each scheme.

### 5. **Personalized Onboarding & Profile**
- **Seamless Registration**: Multi-step onboarding to capture state, district, crop type, and sowing date.
- **Secure Authentication**: Supports both traditional Email/Password and **Google OAuth2** login.

---

## 🛠️ Technical Architecture

### **Backend (FastAPI)**
- **Framework**: High-performance FastAPI with asynchronous service calls (`httpx`, `asyncio`).
- **AI/LLM**: Integrates with **AWS Bedrock** for sophisticated RAG and recommendation logic.
- **Database**: SQLite for local persistence of user profiles, preferences, and chat history.
- **APIs**:
    - **OpenWeatherMap**: For meteorological data.
    - **Data.gov.in (AGMARKNET)**: For market price data.
- **Deployment**: Configured for AWS (ECS/Fargate) with `Dockerfile`, `docker-compose`, and CloudFormation templates.

### **Frontend (Next.js)**
- **Framework**: **Next.js 14** with App Router.
- **Styling**: **Tailwind CSS** for a responsive, mobile-first UI.
- **Animations**: **Framer Motion** for a smooth user experience.
- **State Management**: Lightweight state management for handling user profiles and multilingual translations.
- **I18n**: Custom translation engine supporting English, Hindi, Telugu, Tamil, and Bengali.

---

## 📂 Project Structure

```text
├── app/                  # FastAPI Backend
│   ├── routers/          # API Endpoints (auth, chat, mandi, schemes, today, etc.)
│   ├── services/         # Business Logic (bedrock, mandi, rag, weather, etc.)
│   ├── models/           # Pydantic Schemas (request/response)
│   ├── utils/            # Helpers (exceptions, logging, http_client)
│   └── data/             # Static datasets (onboarding JSON)
├── khetipulse-web/       # Next.js Frontend
│   ├── src/app/          # Pages and Layouts
│   ├── src/components/   # UI Components (Dashboard, Mandi, Onboarding)
│   ├── src/lib/          # Translation logic and API clients
│   └── public/           # Static assets
├── tests/                # Integration and unit tests
└── Dockerfile            # Containerization
```

---

## 🌐 Multilingual Support
KhetiPulse is built from the ground up to be accessible. Current supported languages:
- 🇮🇳 **English**
- 🇮🇳 **Hindi (हिन्दी)**
- 🇮🇳 **Telugu (తెలుగు)**
- 🇮🇳 **Tamil (தமிழ்)**
- 🇮🇳 **Bengali (বাংলা)**

---

## 🛡️ Security & Scalability
- **JWT Authentication**: Secure stateless authentication for all API requests.
- **Structured Logging**: JSON-based logging for production observability.
- **Dependency Injection**: Decoupled architecture for easy testing and service swapping.
- **Cloud Ready**: Includes ECS templates and AWS deployment guides for scaling to millions of users.
