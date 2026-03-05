from app.services.bedrock_service import BedrockService
from app.utils.confidence import calculate_confidence
from app.utils.safety import is_query_safe, get_safety_refusal
from app.utils.exceptions import ExternalServiceError

class RAGService:
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock_service = bedrock_service

    def answer_question(self, question: str, language: str, crop: str = None, location: str = None):
        if not is_query_safe(question):
            return {
                "answer": get_safety_refusal(),
                "confidence_score": 0.0,
                "citations": []
            }

        # Step 1: Retrieve relevant chunks from Bedrock KB
        query_context = f"Crop: {crop}, Location: {location}, Question: {question}"
        try:
            retrieved_results = self.bedrock_service.retrieve_from_kb(query_context)
        except Exception as e:
            # Re-raise as ExternalServiceError to be handled by the global exception handler
            raise ExternalServiceError("Bedrock Knowledge Base", detail=str(e))
        
        if not retrieved_results:
            return {
                "answer": "Not confident. I couldn't find enough reliable information in our database to answer your question. Please consult a local agricultural expert or your nearest Krishi Vigyan Kendra (KVK).",
                "confidence_score": 0.3,
                "citations": []
            }

        # Step 2: Build context for LLM
        context_text = "\n".join([r['content']['text'] for r in retrieved_results])
        citations = [r['location']['s3Location']['uri'] for r in retrieved_results if 'location' in r]

        # Step 3: Invoke LLM
        system_prompt = f"""You are KhetiPulse AI, a senior agricultural consultant.
        Answer the farmer's question using the provided context.
        Language: {language}.
        
        Rules:
        1. If the information is not in the context, say "Not confident. Please consult local KVK."
        2. Provide a 3-step checklist and Do/Don't list for general advice.
        3. IF the user is asking about GOVERNMENT SCHEMES, return the output as a JSON object with:
           "schemes": [
             {{"name": "Scheme Name", "description": "Brief desc", "documents": ["Doc 1", "Doc 2"], "link": "https://..."}},
             {{"name": "Scheme Name 2", "description": "Brief desc 2", "documents": ["Doc 3"], "link": "https://..."}}
           ],
           "answer": "A summary of the recommendations"
        4. For all other questions, return output as a JSON object with keys: "answer", "confidence_score", "checklist", "do", "dont".
        """
        
        prompt = f"Context: {context_text}\n\nQuestion: {question}"
        try:
            response_json = self.bedrock_service.invoke_claude(prompt, system_prompt)
        except Exception as e:
            raise ExternalServiceError("Bedrock LLM", detail=str(e))

        # Step 4: Format Response
        # LLM might return its own confidence, but we combine it with retrieval score
        retrieval_score = retrieved_results[0].get('score', 0.5) if retrieved_results else 0.5
        final_confidence = calculate_confidence(retrieval_score=retrieval_score)

        return {
            "answer": response_json.get("answer", response_json.get("text", "Not confident.")),
            "confidence_score": response_json.get("confidence_score", final_confidence),
            "citations": list(set(citations)),
            "schemes": response_json.get("schemes"),
            "eligible_schemes": response_json.get("eligible_schemes"),
            "documents_required": response_json.get("documents_required"),
            "application_links": response_json.get("application_links")
        }
