# Navigator Memory Package

This package is responsible for the system's learning and memory capabilities, primarily through semantic indexing and retrieval.

## Components

*   **`semantic_indexer.py` - SemanticIndexer (Embedding Model: `mxbai-embed-large` or equivalent `EMBEDDING_MODEL`)**
    *   **Purpose:** Creates vector embeddings for various pieces of information generated during navigation and stores them, allowing for efficient semantic search.
    *   **Key Methods:**
        *   `add_to_memory()`: Takes text content (e.g., a plan step, UI analysis, API request details) and associated metadata, generates a vector embedding using the specified Ollama embedding model, and stores it (currently seems to store in the main SQLite DB, though ideally this would use a dedicated vector store for efficiency at scale).
        *   `search_memory()`: Takes a query string, generates its embedding, and performs a similarity search against the stored vectors to retrieve the most relevant past information.
    *   **Current Implementation:** The current version appears to store embeddings directly in the `learned_info` table in the SQLite database (`ultimate_ai.db`). For larger-scale applications, integrating a dedicated vector database (e.g., ChromaDB, FAISS, Pinecone) would be more appropriate.

## Workflow Integration

The `SemanticIndexer` is used by:

*   `navigator.web_navigator.WebNavigator`: To store UI analysis results and potentially other contextual information during navigation.
*   `navigator.orchestrator.Navigator`: To search for relevant past API interactions or other memories when generating the final summary.
*   Potentially used by the `TaskPlanner` in the future to retrieve relevant past experiences to inform planning. 