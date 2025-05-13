# API Reverse Engineer: Uses DeepSeek LLM for API analysis and inference.
import json
from typing import Dict, Any, Optional

class APIReverseEngineer:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client

    async def analyze_request(self, request_data: str) -> str:
        """Analyze API request data and return insights."""
        prompt = f"Analyze and explain this API request: {request_data}"
        response = await self.ollama_client.generate_text(prompt, model_type="reasoning")
        return response.get('response', '')
    
    async def analyze_request_response_pair(self, 
                                          request_data: Dict[str, Any], 
                                          response_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Thoroughly analyze an API request and its response to understand its purpose,
        authentication mechanisms, parameters, and how it might be reused.
        
        Args:
            request_data: Dictionary containing request details (method, url, headers, body)
            response_data: Optional dictionary containing response details (status_code, body)
            
        Returns:
            Detailed analysis of the API request and response
        """
        analysis_prompt = (
            "Analyze this captured API request and its response as a DeepSeek-R1 expert at reverse engineering APIs.\n\n"
            f"REQUEST:\n{json.dumps(request_data, indent=2)}\n\n"
            f"RESPONSE: {json.dumps(response_data, indent=2) if response_data else 'Not available'}\n\n"
            "Provide analysis covering:\n"
            "1. What is the purpose of this API endpoint?\n"
            "2. What authentication mechanism is used (if any)?\n"
            "3. What are the key parameters and their meaning?\n"
            "4. How could this request be replayed or automated?\n"
            "5. Are there any security concerns or potential optimizations?\n"
        )
        
        response = await self.ollama_client.generate_text(analysis_prompt, model_type="reasoning")
        return response.get('response', 'Failed to analyze API request')
    
    async def infer_api_schema(self, similar_requests: list[Dict[str, Any]]) -> str:
        """
        Given multiple similar API requests, infer the general API schema and pattern.
        
        Args:
            similar_requests: List of related API request dictionaries
            
        Returns:
            Inferred API schema and patterns
        """
        if not similar_requests:
            return "No requests provided for schema inference"
            
        requests_json = json.dumps(similar_requests, indent=2)
        schema_prompt = (
            "You are DeepSeek-R1, an expert at reverse engineering APIs. "
            "Given these similar API requests, infer the general API schema and patterns:\n\n"
            f"{requests_json}\n\n"
            "Please provide:\n"
            "1. The general API schema (endpoint patterns, parameter structures)\n"
            "2. Common headers or authentication patterns\n"
            "3. Required vs optional parameters\n"
            "4. How pagination appears to work (if relevant)\n"
            "5. Any REST/GraphQL/RPC conventions that appear to be followed\n"
        )
        
        response = await self.ollama_client.generate_text(schema_prompt, model_type="reasoning")
        return response.get('response', 'Failed to infer API schema')
