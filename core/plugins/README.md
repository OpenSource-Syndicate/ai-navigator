# Core Plugins Package

This package contains modules that act as wrappers or managers for external tools, services, and APIs used by the Ultimate AI system. Abstracting these interactions into plugins makes the core logic cleaner and allows for easier swapping or extension of these external dependencies.

## Included Plugins

*   **`apis/ollama_client.py` - OllamaClient:**
    *   Provides an asynchronous interface to interact with a running Ollama instance.
    *   Handles API calls to different Ollama endpoints (`/api/generate`, `/api/embeddings`).
    *   Selects the appropriate LLM model based on the requested `model_type` (general, coding, reasoning, embedding) and configured environment variables (`GENERAL_TEXT_MODEL`, `CODING_MODEL`, etc.).
    *   Includes basic error handling (timeouts) and fallback mechanisms (e.g., simulated embeddings if the model doesn't support them).
*   **`selenium_manager.py` - SeleniumManager:**
    *   Manages the lifecycle of the Selenium WebDriver (specifically ChromeDriver).
    *   Handles the complexities of initializing the ChromeDriver, including trying different configurations (direct path vs. `webdriver-manager`, different options) and falling back to a mock driver for testing if initialization fails.
    *   Provides methods for creating and closing the driver instance.
    *   Includes basic browser interaction capabilities like `extract_page_content` (though most interactions are driven by dynamically generated code from the `CodeAssistant`).

## Usage

Instances of these plugin classes are typically created and managed by higher-level components like the `Navigator Orchestrator` and passed down to the components that need them (e.g., `OllamaClient` is passed to all brain agents, `SeleniumManager` is used by `WebNavigator`). 