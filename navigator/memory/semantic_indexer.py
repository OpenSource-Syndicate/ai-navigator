# navigator/memory/semantic_indexer.py
# Uses mxbai-embed-large-v1 for semantic indexing, as per plan.md.

import math
from typing import List, Dict, Any, Optional

# from core.plugins.apis.ollama_client import OllamaClient # Example import

class SemanticIndexer:
    def __init__(self, ollama_client: Any): # Type hint ollama_client more specifically if available
        self.ollama_client = ollama_client
        # In-memory store for embeddings and associated data.
        # Each item: {'id': str, 'text': str, 'embedding': List[float], 'metadata': Optional[Dict]}
        self.memory: List[Dict[str, Any]] = []
        # print("SemanticIndexer initialized.") # Optional: for debugging

    async def _get_embedding(self, text: str) -> List[float]:
        """Generates embedding for the given text using Ollama."""
        if not text:
            print("Warning: Empty text provided for embedding.")
            return [0.0] * 768  # Return a zero vector of default size instead of empty
        try:
            response_data = await self.ollama_client.generate_text(text, model_type="embedding")
            
            # Properly handle different response formats
            if isinstance(response_data, dict):
                # Try to get embedding from expected field
                embedding = response_data.get('embedding')
                
                # If not found, check alternative formats based on model responses
                if embedding is None and 'response' in response_data:
                    # Try to parse embedding from response if it's a list of numbers
                    try:
                        # In case response contains a stringified list
                        resp = response_data.get('response')
                        if isinstance(resp, str) and '[' in resp and ']' in resp:
                            import json
                            embedding = json.loads(resp.replace("'", "\""))
                    except:
                        pass
                
                # If still None, use default zero vector
                if embedding is None:
                    print(f"Warning: No embedding found in response: {response_data}")
                    return [0.0] * 768  # Default embedding size
                    
                # Validate the embedding
                if isinstance(embedding, list) and all(isinstance(x, (int, float)) for x in embedding):
                    return embedding
                else:
                    print(f"Warning: Invalid embedding format: {type(embedding)}")
                    return [0.0] * 768  # Default embedding size
            else:
                print(f"Warning: Unexpected response format: {type(response_data)}")
                return [0.0] * 768  # Default embedding size
        except Exception as e:
            print(f"Error generating embedding for text '{text[:50]}...': {e}")
            return [0.0] * 768  # Default embedding size

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Computes cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(p * q for p, q in zip(vec1, vec2))
        magnitude_vec1_sq = sum(p * p for p in vec1)
        magnitude_vec2_sq = sum(q * q for q in vec2)

        if magnitude_vec1_sq == 0 or magnitude_vec2_sq == 0:
            return 0.0
        
        return dot_product / (math.sqrt(magnitude_vec1_sq) * math.sqrt(magnitude_vec2_sq))

    async def add_to_memory(self, item_id: str, text_content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Generates embedding for the text_content and stores it along with metadata.
        Returns True if successful, False otherwise.
        """
        if not item_id or not text_content:
            # print("Warning: item_id or text_content is empty. Cannot add to memory.") # Optional
            return False
            
        embedding_vector = await self._get_embedding(text_content)
        if not embedding_vector:
            # print(f"Failed to generate embedding for item_id: {item_id}, text: '{text_content[:50]}...'. Item not added.") # Optional
            return False

        if any(item['id'] == item_id for item in self.memory):
            # print(f"Warning: Item with id '{item_id}' already exists in memory. Not adding duplicate.") # Optional
            return False # Or implement update logic

        self.memory.append({
            "id": item_id,
            "text": text_content,
            "embedding": embedding_vector,
            "metadata": metadata or {}
        })
        return True

    async def search_memory(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches memory for items semantically similar to query_text.
        Returns top_k most similar items, including their similarity score.
        """
        if not self.memory:
            return []
        if not query_text:
            return []

        query_embedding = await self._get_embedding(query_text)
        if not query_embedding:
            return []

        scored_items = []
        for item in self.memory:
            item_embedding = item.get("embedding")
            if not item_embedding or not isinstance(item_embedding, list):
                continue
            
            similarity = self._cosine_similarity(query_embedding, item_embedding)
            item_copy = item.copy()
            item_copy['similarity_score'] = similarity
            scored_items.append(item_copy)
        
        scored_items.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_items[:top_k]

    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an item from memory by its ID."""
        for item in self.memory:
            if item["id"] == item_id:
                return item
        return None

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Retrieves all items currently in memory."""
        return list(self.memory) # Return a copy

    def clear_memory(self) -> None:
        """Clears all items from the in-memory store."""
        self.memory = []

    def __len__(self) -> int:
        """Returns the number of items in memory."""
        return len(self.memory)
