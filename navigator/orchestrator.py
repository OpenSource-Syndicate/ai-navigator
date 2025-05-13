# Navigator Orchestrator
# Implements the multi-model approach outlined in plan.md

from navigator.brain.code_assistant import CodeAssistant
from navigator.brain.planner import TaskPlanner
from navigator.brain.api_reverse_engineer import APIReverseEngineer
from navigator.memory.semantic_indexer import SemanticIndexer
from navigator.web_navigator import WebNavigator
from core.plugins.selenium_manager import SeleniumManager

class Navigator:
    def __init__(self, ollama_client, selenium_manager: SeleniumManager = None):
        """
        Initialize the Navigator orchestrator to coordinate all models.
        
        Args:
            ollama_client: Client for communicating with Ollama API
            selenium_manager: Optional SeleniumManager instance
        """
        self.ollama_client = ollama_client
        
        # Create a new SeleniumManager if none was provided
        if selenium_manager is None:
            self.selenium_manager = SeleniumManager(headless=False)
        else:
            self.selenium_manager = selenium_manager

        # Individual components (can still be used directly if needed)
        self.code_assistant = CodeAssistant(ollama_client)  # Granite-Code:8B
        self.planner = TaskPlanner(ollama_client)           # Hermes-3
        self.api_reverse_engineer = APIReverseEngineer(ollama_client)  # DeepSeek-R1 8B
        self.semantic_indexer = SemanticIndexer(ollama_client)  # mxbai-embed-large-v1

        # Main navigator component that uses the others
        self.web_navigator = WebNavigator(
            ollama_client, 
            self.selenium_manager, 
            db_session_factory=self._get_db_session_for_navigator
        )

    def _get_db_session_for_navigator(self):
        """Get a database session."""
        from core.database.database import SessionLocal
        return SessionLocal()

    async def perform_web_goal(self, user_goal: str):
        """
        Main entry point: orchestrates the multi-model system to achieve a user's web-related goal.
        
        This implements the flow in plan.md:
        1. Hermes-3 creates a plan
        2. Granite-Code generates the execution code
        3. As actions are taken, requests are captured
        4. DeepSeek-R1 analyzes the API interactions
        5. mxbai-embed stores and connects the semantic knowledge
        
        Args:
            user_goal: The user's goal expressed in natural language
        """
        print(f"Navigator (Orchestrator) received web goal: {user_goal}")
        try:
            # Step 1: Initial planning using Hermes-3 via TaskPlanner
            initial_context = "Starting a new browsing session."
            initial_plan = await self.planner.plan(user_goal, context=initial_context)
            print(f"Initial plan:\n{initial_plan}")
            
            # Step 2: Execute the plan using WebNavigator
            # (which will use all our components internally)
            await self.web_navigator.navigate_and_learn(user_goal)
            
            # Step 3: Summarize what was learned
            summary = await self.summarize_results(user_goal)
            print(f"Summary of learnings:\n{summary}")
            
        finally:
            # Always ensure browser is closed
            self.web_navigator.close_browser()
        
        print(f"Navigator (Orchestrator) finished web goal: {user_goal}")
    
    async def summarize_results(self, user_goal: str) -> str:
        """
        Get a summary of the navigation and what was learned.
        
        Args:
            user_goal: The original user goal
            
        Returns:
            A natural language summary of what was learned
        """
        # Get recent memories related to this goal
        memories = await self.semantic_indexer.search_memory(user_goal, top_k=10)
        
        # Extract captured APIs
        api_memories = [m for m in memories if m.get('metadata', {}).get('type') == 'api_request']
        
        # Format API info for the prompt
        api_info = ""
        if api_memories:
            api_info = "APIs discovered:\n"
            for i, api in enumerate(api_memories):
                api_info += f"{i+1}. {api.get('text', '')[:200]}...\n"
        
        # Get summary from Hermes
        prompt = (
            f"Summarize what was learned while pursuing this goal: '{user_goal}'\n\n"
            f"{api_info}\n"
            "Focus on:\n"
            "1. What was accomplished\n"
            "2. What APIs or patterns were discovered\n"
            "3. What might be useful for future automation\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        return response.get('response', 'No summary available.')
    
    async def api_search(self, query: str) -> list:
        """
        Search for API patterns matching a specific query.
        
        Args:
            query: The search query
            
        Returns:
            List of matching API memories
        """
        return await self.semantic_indexer.search_memory(query, top_k=5)
    
    async def generate_code_for_task(self, task_description: str) -> str:
        """
        Direct access to the code generator for a specific task.
        
        Args:
            task_description: Description of the task to code
            
        Returns:
            Generated code as text
        """
        return await self.code_assistant.generate_code(task_description)
