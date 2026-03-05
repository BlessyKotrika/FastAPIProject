# AWS Configuration Guide for KhetiPulse Backend

This document provides the step-by-step configuration required on the AWS side to enable all AI and data features of the KhetiPulse system.

---

### 1. Enable Amazon Bedrock Model Access (Critical)
Before the code can call any AI services, you **must** enable model access in your AWS account.
1.  Log in to the **AWS Console**.
2.  Search for **Amazon Bedrock**.
3.  On the left sidebar, click **Model Access**.
4.  Click **Edit** and request access for:
    *   **Anthropic**: Claude 3 Haiku
    *   **Amazon**: Titan Text Embeddings v2
5.  *Note: This might take a few minutes to be approved.*

---

### 2. Set Up Bedrock Knowledge Base (RAG)
This powers the "Ask KhetiPulse" and "Scheme Helper" features.
1.  **S3 Bucket for Docs**: Create a bucket (e.g., `khetipulse-documents`) and upload your agricultural PDF/DOCX advisories.
2.  **Create Knowledge Base**:
    *   Go to Bedrock Console > Knowledge Bases > **Create**.
    *   **Data Source**: Select the S3 bucket you just created.
    *   **Embeddings Model**: Select **Titan Text Embeddings v2**.
    *   **Vector Store**: Choose **Quick create a new vector store** (this sets up OpenSearch Serverless for you).
3.  **Sync**: Once created, click **Sync** to index your documents.
4.  **ID**: Copy the `Knowledge Base ID` and add it to your `.env` file as `BEDROCK_KB_ID`.

---

### 3. S3 Bucket for Mandi Data
1.  The SAM template creates a bucket named `khetipulse-data-<account-id>-<region>`.
2.  Ensure you have this bucket name in your `.env` file as `S3_BUCKET_NAME`.
3.  *(Optional)* If you are not using the live API for some crops, upload a CSV named `agmarknet_latest.csv`.

---

### 4. DynamoDB Tables
The system expects two tables. If you deploy using `sam deploy`, these are created automatically. If creating manually:
1.  **Table: `Users`**
    *   Partition Key: `user_id` (String)
2.  **Table: `AdvisoryHistory`**
    *   Partition Key: `user_id` (String)
    *   Sort Key: `timestamp` (String)

---

### 5. IAM Permissions (For Local Testing)
Your local AWS User (configured via `aws configure`) must have a policy attached with these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:Retrieve",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

---

### 6. Summary of Environment Variables (.env)
After setting up the above, your `.env` should look like this:

| Variable | Description |
| :--- | :--- |
| `AWS_REGION` | e.g., `us-east-1` |
| `BEDROCK_KB_ID` | From Step 2 |
| `OPENWEATHER_API_KEY` | Your key from OpenWeatherMap |
| `AGMARKNET_API_KEY` | `579b464db66ec23bdd000001fee029797c5f45b9462e3f8d384d4730` |
| `DYNAMODB_TABLE_USERS` | `Users` |
| `S3_BUCKET_NAME` | Your bucket name |

---

### 7. Deployment
Once the above are configured, run:
```bash
sam build
sam deploy --guided
```
