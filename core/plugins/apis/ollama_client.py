import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.base_url = "http://172.30.45.64:11434/api"
        # Get model names from environment with defaults
        self.general_model = os.getenv("GENERAL_TEXT_MODEL", "hermes-3")
        self.coding_model = os.getenv("CODING_MODEL", "granite-code-8b")  # Fixed typo in env var name
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large-v1")
        self.reasoning_model = os.getenv("REASONING_MODEL", "deepseek-r1-8b")
    
    async def generate_text(self, prompt: str, model_type: str = "general"):
        """
        Generate text using the appropriate Ollama model based on the task type.
        
        Args:
            prompt: The prompt to send to the model
            model_type: Type of generation (general, coding, embedding, reasoning)
            
        Returns:
            JSON response from Ollama API
        """
        model = self._get_model_for_type(model_type)
        
        # Special handling for embeddings which use a different endpoint
        if model_type == "embedding":
            return await self._get_embedding(prompt, model)
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                return response.json()
            except httpx.ReadTimeout:
                print(f"Ollama server request timed out. Using fallback response.")
                return {"response": f"[Fallback response - Ollama timeout for {model_type}]"}
            except Exception as e:
                print(f"Error calling Ollama API: {e}")
                return {"response": f"[Error response - {str(e)}]"}
    
    def _get_model_for_type(self, model_type: str) -> str:
        """
        Get the appropriate model name for the specified type.
        
        Args:
            model_type: Type of model needed (general, coding, embedding, reasoning)
            
        Returns:
            Model name to use with Ollama
        """
        model_map = {
            "general": self.general_model,
            "coding": self.coding_model,
            "embedding": self.embedding_model,
            "reasoning": self.reasoning_model
        }
        return model_map.get(model_type, self.general_model)

    async def _get_embedding(self, text: str, model: str):
        """
        Get embeddings for text using the embeddings endpoint.
        
        Args:
            text: Text to embed
            model: Model to use
            
        Returns:
            Dictionary containing embedding
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    json={
                        "model": model,
                        "prompt": text
                    }
                )
                result = response.json()
                
                # Return a simulated embedding if model doesn't support embeddings
                if "error" in result:
                    print(f"Embedding error: {result.get('error')}")
                    # Create a pseudo-random but deterministic embedding based on the text
                    import hashlib
                    import struct
                    
                    # Generate a deterministic seed from the text
                    hash_obj = hashlib.md5(text.encode('utf-8'))
                    seed = struct.unpack('<Q', hash_obj.digest()[:8])[0]
                    
                    # Use the seed to generate pseudo-random values
                    import random
                    random.seed(seed)
                    
                    # Generate 768-dimensional embedding (common dimension)
                    embedding = [random.uniform(-1, 1) for _ in range(768)]
                    
                    # Normalize the embedding
                    import math
                    magnitude = math.sqrt(sum(x*x for x in embedding))
                    normalized = [x/magnitude for x in embedding]
                    
                    return {"embedding": normalized}
                
                return result
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a zero vector as fallback
            return {"embedding": [0.0] * 768}
