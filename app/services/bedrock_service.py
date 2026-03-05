import json
from typing import Dict, List, Any
import boto3
from app.config import settings

class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.AWS_REGION
        )
        self.kb_client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=settings.AWS_REGION
        )

    def invoke_claude(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Invokes Claude 3 Haiku with a prompt and returns structured JSON."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        })

        try:
            response = self.client.invoke_model(
                modelId=settings.CLAUDE_MODEL_ID,
                body=body
            )
            response_body = json.loads(response.get("body").read())
            text_content = response_body["content"][0]["text"]
            # Attempt to parse JSON from response
            try:
                return json.loads(text_content)
            except json.JSONDecodeError:
                # Fallback if LLM didn't return pure JSON
                return {"text": text_content}
        except Exception as e:
            print(f"Error invoking Bedrock: {e}")
            return {"error": str(e)}

    def retrieve_from_kb(self, query: str, kb_id: str = settings.BEDROCK_KB_ID):
        """Retrieves relevant chunks from Bedrock Knowledge Base."""
        if not kb_id:
            return []
        
        try:
            response = self.kb_client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            )
            return response.get('retrievalResults', [])
        except Exception as e:
            print(f"Error retrieving from KB: {e}")
            return []

bedrock_service = BedrockService()
