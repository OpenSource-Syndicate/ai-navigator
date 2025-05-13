# Navigator Brain Package

This package houses the specialized Large Language Model (LLM) agents, each responsible for a specific cognitive task within the web navigation and automation process. These agents are invoked by the `Navigator Orchestrator` or the `WebNavigator`.

## AI Agents

*   **`planner.py` - TaskPlanner (Model: Hermes-3 or equivalent `GENERAL_TEXT_MODEL`)**
    *   **Purpose:** Responsible for high-level planning, reasoning about web UIs, and error handling.
    *   **Key Methods:**
        *   `create_detailed_plan()`: Takes a user goal, current browser context (URL, page content sample), and API history to generate a step-by-step plan for web automation using Selenium.
        *   `analyze_ui()`: Analyzes HTML page content to identify the page's purpose, key interactive elements, navigation options, and authentication requirements.
        *   `handle_error()`: Given an error context and the original goal, it attempts to diagnose the issue and propose a recovery plan.

*   **`code_assistant.py` - CodeAssistant (Model: Granite-Code or equivalent `CODING_MODEL`)**
    *   **Purpose:** Generates and fixes Python code, primarily for Selenium-based browser automation and API request replay.
    *   **Key Methods:**
        *   `generate_selenium_code()`: Generates a Python Selenium code snippet to achieve a specific, fine-grained goal (e.g., "click button with text 'Login'", "type 'testuser' into input with name 'username'") based on the current URL, page content, and previous actions.
        *   `fix_code()`: Attempts to debug and fix a provided Python code snippet based on an error message.
        *   `generate_api_replay_code()`: Generates Python code (using `requests`, `httpx`, etc.) to replay a captured API request.

*   **`api_reverse_engineer.py` - APIReverseEngineer (Model: DeepSeek-R1 or equivalent `REASONING_MODEL`)**
    *   **Purpose:** Analyzes captured HTTP network traffic to understand API structures, infer schemas, and identify automation opportunities.
    *   **Key Methods:**
        *   `analyze_request_response_pair()`: Provides a detailed analysis of a single HTTP request and its corresponding response, covering purpose, authentication, parameters, and replayability.
        *   `infer_api_schema()`: Given a list of similar API requests, it attempts to infer the general API schema, common patterns, and parameter structures.

## Interaction

These brain components are primarily used by:

*   `navigator.orchestrator.Navigator`: For initial planning and final summarization.
*   `navigator.web_navigator.WebNavigator`: For generating Selenium code for individual plan steps, analyzing UI during navigation, and potentially for error handling during step execution.

Each agent communicates with the respective LLM via the `OllamaClient` to get responses based on carefully crafted system prompts that define their persona and task. 