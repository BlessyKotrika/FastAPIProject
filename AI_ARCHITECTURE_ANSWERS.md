### KhetiPulse: AI and Architecture Overview

This document provides a detailed technical overview of how AI and AWS services are integrated into the KhetiPulse solution to empower farmers with data-driven decision support.

#### 1. Why AI is required in your solution?
AI is the core engine of KhetiPulse, enabling it to move beyond a static information portal to a dynamic, responsive decision-support system. It is required for:
- **Natural Language Understanding (NLU):** To interpret complex, multilingual queries from farmers (e.g., "paddy pest control" vs. "current mandi prices for rice") and route them to the correct data source (Mandi API vs. Knowledge Base).
- **Intelligent Synthesis:** Merging disparate data points—such as real-time weather forecasts from OpenWeatherMap, crop-specific growth stages, and historical advisory bulletins—into actionable "Do/Avoid/Prepare" cards.
- **Contextual Grounding (RAG):** Using Retrieval-Augmented Generation to ensure that the advice provided is not just general LLM knowledge but is strictly grounded in verified agricultural documents stored in the Amazon Bedrock Knowledge Base.

#### 2. How AWS services are used within your architecture?
The architecture is built natively on AWS to ensure scalability, security, and low-latency AI inference:
- **Amazon Bedrock:** Serves as the primary AI layer. It hosts the **Claude 3 Haiku** model for text generation/reasoning and uses **Titan Embeddings** for the RAG-based Knowledge Base.
- **AWS Secrets Manager:** Securely stores and manages sensitive API keys (OpenWeather, Agmarknet), database credentials, and JWT secret keys.
- **Amazon DynamoDB:** A NoSQL database used for storing persistent data like user profiles and advisory history for session tracking.
- **Amazon S3:** Used for hosting static assets and storing the source documents that populate the Bedrock Knowledge Base.
- **AWS ECS / Lambda:** The backend is designed for containerized deployment (via ECS) or serverless execution (via Lambda with the Mangum adapter).

#### 3. What value the AI layer adds to the user experience?
The AI layer transforms the user experience from "searching for information" to "receiving personalized guidance":
- **Personalized Actionability:** Instead of checking weather and guessing what to do, the AI tells the farmer exactly what to "Avoid Today" (e.g., "Don't spray pesticides because rain is expected in 4 hours").
- **Multilingual Accessibility:** The AI handles language translation and localized responses, making expert agricultural advice accessible to farmers in their native languages.
- **Trust and Reliability:** Through the RAG pipeline, the AI provides citations for its answers, increasing the farmer's confidence in the advice provided.
- **Simplified Interface:** A conversational chat interface ("Ask KhetiPulse") allows farmers to interact with complex data systems using natural language, removing the technical barrier of navigating complex applications.
