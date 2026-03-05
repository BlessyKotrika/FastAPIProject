# KhetiPulse Web Frontend (Next.js)

This is a mobile-friendly, responsive web frontend for KhetiPulse, built with Next.js, Tailwind CSS, and Zustand.

## 🚀 Features
- **Mobile-First Design**: Optimized for 360px+ screens.
- **Onboarding Wizard**: Collects farm and location details for personalization.
- **AI Advisor**: RAG-powered chatbot for farming advice.
- **Mandi Insights**: Real-time market prices and trends.
- **Offline Mode**: Persistent state and offline banners.
- **Multilingual UI**: Support for English, Hindi, Telugu, Tamil, and Bengali.

## 🛠️ Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **State Management**: Zustand (with Persist)
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **API Client**: Axios

## 📦 Getting Started

1.  **Navigate to the frontend directory**:
    ```bash
    cd khetipulse-web
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Configure Environment**:
    Create a `.env.local` file:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

4.  **Run Development Server**:
    ```bash
    npm run dev
    ```
    Open [http://localhost:3000](http://localhost:3000) to view the app.

## 🔗 Backend Integration
The frontend integrates with the FastAPI backend endpoints:
- `POST /today/` -> Dashboard
- `POST /sell-smart/` -> Mandi Insights
- `POST /chat/` -> AI Advisor
- `POST /preferences/language` -> User Profile

## 🏗️ Project Structure
- `src/app`: Pages and routing
- `src/components`: Reusable UI components (Layout, Onboarding)
- `src/services`: API client and services
- `src/lib`: Global state and utilities

## 🌐 Build for Production
```bash
npm run build
npm run start
```
