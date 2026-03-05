# KhetiPulse Local Setup & Execution Guide

This guide provides step-by-step instructions to set up and run the KhetiPulse AI platform (Backend and Frontend) on your local machine.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed:
1.  **Python 3.9 or higher**: [Download here](https://www.python.org/downloads/)
2.  **Node.js 18.x or higher**: [Download here](https://nodejs.org/) (includes `npm`)
3.  **AWS CLI**: [Install and Configure](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
4.  **Git**: [Download here](https://git-scm.com/)

---

## 🏗️ Step 1: Backend Setup (FastAPI)

The backend is a production-grade FastAPI application with structured logging and dependency injection.

1.  **Open your terminal** and navigate to the project root:
    ```bash
    cd /path/to/FastAPIProject
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    # Create the environment
    python3 -m venv venv

    # Activate it (macOS/Linux)
    source venv/bin/activate

    # Activate it (Windows)
    # .\venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your credentials (refer to `.env.example`):
    ```env
    AWS_ACCESS_KEY_ID=your_key
    AWS_SECRET_ACCESS_KEY=your_secret
    AWS_REGION=us-east-1
    BEDROCK_KB_ID=your_kb_id
    OPENWEATHER_API_KEY=your_weather_key
    
    # Google Auth (Get from Google Cloud Console)
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    ```

5.  **Authentication Setup**:
    KhetiPulse supports both local ID/Password login and Google OAuth2.
    - **Local Login**: No additional setup required! Just register a new account on the Login page.
    - **Google OAuth2 (Optional)**:
        1. Go to [Google Cloud Console](https://console.cloud.google.com/).
        2. Create a new project (e.g., `KhetiPulse`).
        3. Navigate to **APIs & Services > Credentials**.
        4. Click **Create Credentials > OAuth client ID**.
        5. Application type: `Web application`.
        6. Authorized JavaScript origins: `http://localhost:3000`.
        7. Authorized redirect URIs: `http://localhost:3000`.
        8. Copy the **Client ID** and **Client Secret** to your `.env` (Backend) and `khetipulse-web/.env.local` (Frontend) files.

6.  **Start the Backend Server**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    *   The API will be available at: `http://localhost:8000`
    *   Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 💻 Step 2: Frontend Setup (Next.js)

The frontend is built with Next.js 14, Tailwind CSS, and Framer Motion.

1.  **Open a NEW terminal window** (leave the backend running).
2.  **Navigate to the frontend directory**:
    ```bash
    cd khetipulse-web
    ```

3.  **Install Node.js dependencies**:
    ```bash
    npm install
    ```

4.  **Configure `.env.local`**:
    Ensure a `.env.local` file exists in the `khetipulse-web/` folder with the following:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
    ```

5.  **Start the Development Server**:
    ```bash
    npm run dev
    ```
    *   The application will be available at: `http://localhost:3000`

---

## ✅ Step 3: Verification & Testing

### 1. Automated API Test
While the backend is running, you can run the included test script to verify all core endpoints (Weather, Mandi, RAG Chat, Schemes):
```bash
# From the project root
chmod +x tests/test_endpoints.sh
./tests/test_endpoints.sh
```

### 2. Manual Verification
*   Open your browser to [http://localhost:3000](http://localhost:3000).
*   **Create an Account**: Since you don't have Google login, use the **Register** tab to create a local username and password.
*   Complete the **Onboarding Wizard**.
*   Verify that the **Dashboard** displays weather alerts and the **Mandi Insights** show real-time prices.
*   Ask a question in the **AI Advisor** chat.

---

## 🛠️ Troubleshooting

*   **ModuleNotFoundError**: Ensure your virtual environment is activated and `pip install -r requirements.txt` completed without errors.
*   **CORS Issues**: The backend is configured to allow origins from `*`. If you face issues, ensure the frontend is hitting `localhost:8000`.
*   **AWS Permissions**: Ensure your AWS user has `AmazonBedrockFullAccess` and permissions for DynamoDB and S3 as specified in `app/config.py`.
