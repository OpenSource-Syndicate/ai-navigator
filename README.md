#  AI - Web Navigator

This project implements an intelligent web navigation and automation system using a multi-model Large Language Model (LLM) architecture. It can understand user goals expressed in natural language, plan and execute web browsing tasks, interact with web elements, analyze network requests, and learn from its interactions.

## Architecture

The system employs a modular, multi-LLM approach inspired by the concepts outlined in `plan.md`. Each LLM specializes in a specific task:

1.  **Task Planner (`Hermes-3` - configured via `GENERAL_TEXT_MODEL` env var):** Receives the user's high-level goal and generates a detailed, step-by-step plan for web navigation and interaction. It considers the current browser state (URL, page content) and past API interactions.
2.  **Code Assistant (`Granite-Code` - configured via `CODING_MODEL` env var):** Takes individual steps from the plan and generates the corresponding Python code (using Selenium) to execute that action in the browser (e.g., clicking buttons, filling forms). It also assists with fixing code errors and generating API replay scripts.
3.  **API Reverse Engineer (`DeepSeek-R1` - configured via `REASONING_MODEL` env var):** Analyzes captured HTTP requests and responses during navigation to understand API endpoints, authentication, parameters, and potential automation opportunities.
4.  **Semantic Indexer (`mxbai-embed-large` - configured via `EMBEDDING_MODEL` env var):** Creates vector embeddings of plans, actions, UI analyses, and captured API requests. This allows for semantic search over the system's memory to find relevant past interactions or similar patterns.

These models are coordinated by the **Navigator Orchestrator (`navigator/orchestrator.py`)**, which manages the overall flow: Plan -> Execute (via Code Generation & Selenium) -> Analyze -> Learn (via Indexing).

**Core Components:**

*   **`navigator/`**: Contains the main orchestration and AI logic.
    *   `orchestrator.py`: The central coordinator.
    *   `web_navigator.py`: Manages browser interaction via Selenium and coordinates code generation/execution for plan steps.
    *   `brain/`: Houses the specialized LLM agents (Planner, Code Assistant, API Reverse Engineer).
    *   `memory/`: Handles semantic indexing and retrieval of learned information.
*   **`core/`**: Provides shared utilities and plugins.
    *   `plugins/`: Contains wrappers for external tools/APIs (Selenium Manager, Ollama Client).
    *   `database/`: Manages the SQLite database for storing learned information and API requests.
*   **`main.py`**: A FastAPI application providing an API interface to the Navigator.
*   **`real_testing.py`**: A command-line script for testing the Navigator with specific prompts.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Likhithsai2580/ai-navigator
    cd ai-navigator
    ```

2.  **Install dependencies:**
    This project uses `uv` for package management.
    ```bash
    # Install uv if you haven't already
    pip install uv
    # Create a virtual environment and install dependencies
    uv venv
    uv pip install -r requirements.txt
    # Activate the environment (example for bash/zsh)
    source .venv/bin/activate 
    # (or .venv\Scripts\activate on Windows)
    ```

3.  **Set up Ollama:**
    *   Ensure you have Ollama installed and running. See [Ollama Website](https://ollama.com/).
    *   Pull the required models (names can be configured via environment variables, defaults shown):
        ```bash
        ollama pull hermes-3 # Or your GENERAL_TEXT_MODEL
        ollama pull granite-code:8b # Or your CODING_MODEL
        ollama pull deepseek-r1:8b # Or your REASONING_MODEL
        ollama pull mxbai-embed-large # Or your EMBEDDING_MODEL
        ```
    *   Verify the Ollama server is accessible from the project environment. The default URL used is `http://<ollama-host>:11434/api` (check `core/plugins/apis/ollama_client.py`). If running Ollama in WSL and the project on Windows, ensure the correct IP address is used.

4.  **Environment Variables:**
    Create a `.env` file in the project root or set environment variables directly. These configure the Ollama models used:
    ```dotenv
    # .env file
    # Replace with the exact names from 'ollama list' if different
    GENERAL_TEXT_MODEL=hermes-3 
    CODING_MODEL=granite-code:8b
    REASONING_MODEL=deepseek-r1:8b
    EMBEDDING_MODEL=mxbai-embed-large
    ```

5.  **Initialize Database:**
    The project uses a SQLite database (`ultimate_ai.db`). It should be created automatically, but you can ensure it's set up by running:
    ```bash
    uv run python init_db.py 
    ```

## Usage

There are two main ways to interact with the system:

1.  **Command-Line Testing (`real_testing.py`):**
    Use this script for quick tests with a specific goal.
    ```bash
    uv run python real_testing.py --prompt "Your web goal here" 
    
    # Example:
    uv run python real_testing.py --prompt "Search DuckDuckGo for recent AI news"
    ```
    This will run the full orchestration process for the given prompt.

2.  **FastAPI Application (`main.py`):**
    Provides a web API for more structured interaction.
    ```bash
    # Start the FastAPI server
    uv run uvicorn main:app --reload 
    ```
    Access the API documentation at `http://127.0.0.1:8000/docs`. Key endpoints include:
    *   `/navigate` (POST): Starts a background task to achieve a web goal.
    *   `/generate` (POST): Simple text generation via Ollama.
    *   `/api/search` (GET): Search the memory for stored API patterns.
    *   `/memory/search` (GET): Perform a semantic search over the learned memory.

## Future Plans

See `future_plans.md` for planned improvements and features.
