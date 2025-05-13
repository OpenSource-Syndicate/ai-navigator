# Navigator Package

This package contains the core orchestration logic for the multi-model AI web navigation system.

## Submodules

*   **`orchestrator.py`**: 
    *   The central `Navigator` class that coordinates the different AI models and manages the overall workflow for achieving a user's web goal.
    *   Implements the main flow: Plan -> Execute -> Analyze -> Learn.
    *   Initializes and holds instances of the different brain components, memory indexer, and the web navigator.
*   **`web_navigator.py`**: 
    *   The `WebNavigator` class responsible for direct browser interaction using Selenium.
    *   Executes the steps provided by the Planner by invoking the Code Assistant to generate Selenium code.
    *   Captures page content and potentially network requests (though network request capture isn't fully implemented here yet).
    *   Manages the Selenium driver lifecycle.
*   **`brain/`**: 
    *   Contains the specialized LLM agent classes.
    *   See `navigator/brain/README.md` for details.
*   **`memory/`**: 
    *   Handles the storage and retrieval of learned information using semantic vector embeddings.
    *   See `navigator/memory/README.md` for details.

## Workflow

1.  A user goal is passed to `Navigator.perform_web_goal()` in `orchestrator.py`.
2.  The Orchestrator gathers initial context (current URL, page content, API history) from the `WebNavigator`.
3.  The Orchestrator asks the `TaskPlanner` (`brain/planner.py`) to create a detailed step-by-step plan.
4.  The Orchestrator passes the goal and the plan to `WebNavigator.navigate_and_learn()`.
5.  The `WebNavigator` iterates through the plan steps:
    *   For each step, it asks the `CodeAssistant` (`brain/code_assistant.py`) to generate the necessary Selenium code.
    *   It executes the generated Selenium code using the `SeleniumManager`.
    *   It updates its state (current URL, page content).
    *   (Future enhancement: It could trigger API analysis via `APIReverseEngineer`)
    *   It adds relevant information (UI analysis, executed steps) to the `SemanticIndexer` (`memory/semantic_indexer.py`).
6.  After navigation, the Orchestrator asks the `SemanticIndexer` for relevant memories and uses the `TaskPlanner` to generate a summary of what was learned.
7.  The Orchestrator ensures the browser is closed via the `WebNavigator`. 