# KhetiPulse - Full Application Run Guide

This guide explains how to run both the **FastAPI Backend** and the **Next.js Frontend** for the KhetiPulse application.

---

## 🏗️ Step 1: AWS Setup (Backend Prerequisite)
Before running the code, ensure your AWS environment is ready.
1.  **Enable Bedrock Models**: Go to AWS Bedrock Console and request access for **Claude 3 Haiku** and **Titan Text Embeddings v2**.
2.  **Configure AWS CLI**: Run `aws configure` in your terminal and enter your `Access Key`, `Secret Key`, and `Region (e.g., us-east-1)`.
3.  **Sync Knowledge Base**: Ensure your Bedrock Knowledge Base is created and synced with your S3 documentation.

---

## 🚀 Step 2: Run the FastAPI Backend

1.  **Open a terminal** and navigate to the project root.
2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure `.env`**: Ensure your `.env` file in the root directory has your AWS keys and service IDs (see `.env.example`).
5.  **Start the server**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    *The backend will be available at `http://localhost:8000`.*

---

## 💻 Step 3: Run the Next.js Frontend

1.  **Open a NEW terminal window** (keep the backend terminal running).
2.  **Navigate to the frontend directory**:
    ```bash
    cd khetipulse-web
    ```
3.  **Install Node.js dependencies**:
    ```bash
    npm install
    ```
4.  **Configure `.env.local`**:
    Create a file named `.env.local` in `khetipulse-web/` and add:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
5.  **Start the development server**:
    ```bash
    npm run dev
    ```
    *The frontend will be available at `http://localhost:3000`.*

---

## 📱 Step 4: Access the Application

1.  Open your browser and go to **[http://localhost:3000](http://localhost:3000)**.
2.  You will be greeted by the **Onboarding Wizard**.
3.  Select your language (Hindi, Telugu, English, etc.) and enter your farm details.
4.  Explore the **Dashboard**, **Mandi Insights**, and **AI Advisor** tabs!

---

## 🛠️ Troubleshooting

- **CORS Error**: Ensure the backend is running at port 8000 and the frontend at 3000. The FastAPI app is configured to allow origins from `*` for local development.
- **AWS Credentials**: If the AI Advisor says "Not confident" or gives a "Security Token" error, check your `aws sts get-caller-identity` in the backend terminal.
- **Node.js Version**: Use Node.js 18.x or higher for the frontend.
