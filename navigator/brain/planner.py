# Task Planner: Uses Hermes-3 LLM for high-level planning and reasoning.
from typing import List, Dict, Any, Optional

class TaskPlanner:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client

    async def plan(self, user_goal: str, context: str = "") -> str:
        """
        Create a high-level plan to achieve a user goal.
        
        Args:
            user_goal: The goal specified by the user
            context: Additional context information
            
        Returns:
            Step-by-step plan as text
        """
        prompt = f"Plan the steps to achieve: {user_goal}\nContext: {context}"
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        return response.get('response', '')
    
    async def create_detailed_plan(self, 
                                 user_goal: str, 
                                 current_url: str = "", 
                                 page_content: str = "", 
                                 api_history: List[Dict[str, Any]] = None) -> str:
        """
        Create a detailed, step-by-step plan for web navigation and API interaction.
        
        Args:
            user_goal: The goal specified by the user
            current_url: Current URL if in a browser session
            page_content: Current page content or summary
            api_history: Previously seen API requests
            
        Returns:
            Detailed, executable plan
        """
        # Handle None values
        if page_content is None:
            page_content = ""
        if api_history is None:
            api_history = []
            
        # Limit page content to avoid token overflow
        page_content_sample = page_content[:1500] + "..." if len(page_content) > 1500 else page_content
        
        api_history_str = ""
        if api_history:
            api_history_str = "Previously observed API patterns:\n"
            for i, api in enumerate(api_history[:5]):  # Limit to 5 recent APIs
                api_history_str += f"{i+1}. {api.get('method', 'Unknown')} {api.get('url', 'Unknown')}\n"
        
        prompt = (
            "As Hermes-3, create a detailed step-by-step plan to achieve this web automation goal:\n\n"
            f"GOAL: {user_goal}\n\n"
            f"CURRENT STATE:\n- URL: {current_url or 'No current URL'}\n- Page content sample: {page_content_sample}\n\n"
            f"{api_history_str}\n\n"
            "Your plan should:\n"
            "1. Break down the goal into clear, executable steps\n"
            "2. Identify key UI elements that need to be interacted with\n"
            "3. Anticipate potential challenges and include fallback approaches\n"
            "4. Consider the most efficient path to the goal\n"
            "5. Structure your response as a numbered list of steps\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        return response.get('response', '')
    
    async def analyze_ui(self, page_content: str, current_url: str = "") -> Dict[str, Any]:
        """
        Analyze a webpage UI to identify key interactive elements and their purpose.
        
        Args:
            page_content: HTML content of the current page
            current_url: Current URL
            
        Returns:
            Dictionary with UI analysis results
        """
        # Handle None values
        if page_content is None:
            page_content = ""
            
        # Limit page content to avoid token overflow
        page_content_sample = page_content[:3000] + "..." if len(page_content) > 3000 else page_content
        
        prompt = (
            "Analyze this webpage UI and identify key interactive elements.\n\n"
            f"URL: {current_url or 'No URL'}\n\n"
            f"PAGE CONTENT:\n{page_content_sample}\n\n"
            "Provide a structured analysis that includes:\n"
            "1. Main purpose of this page\n"
            "2. Key interactive elements (buttons, forms, links) and their likely functions\n"
            "3. Navigation options available\n"
            "4. Any authentication or input requirements\n"
            "5. Overall page structure\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        analysis = response.get('response', '')
        
        # Extract structured information from the analysis
        # This is a simplified approach - in production, you might want to use
        # a more structured prompt or parsing approach
        result = {
            "page_purpose": "",
            "interactive_elements": [],
            "navigation_options": [],
            "auth_requirements": [],
            "full_analysis": analysis
        }
        
        return result
    
    async def handle_error(self, 
                         error_context: str, 
                         original_goal: str, 
                         steps_completed: List[str]) -> str:
        """
        Generate a recovery plan when an error occurs during web automation.
        
        Args:
            error_context: Description of the error that occurred
            original_goal: The original goal being pursued
            steps_completed: List of steps successfully completed
            
        Returns:
            Recovery plan as text
        """
        # Handle None values
        if steps_completed is None:
            steps_completed = []
            
        steps_completed_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps_completed)])
        
        prompt = (
            "An error occurred during web automation. Help create a recovery plan.\n\n"
            f"ORIGINAL GOAL: {original_goal}\n\n"
            f"STEPS COMPLETED:\n{steps_completed_str or 'No steps completed'}\n\n"
            f"ERROR: {error_context}\n\n"
            "Please provide:\n"
            "1. Analysis of what might have gone wrong\n"
            "2. Alternate approaches to try\n"
            "3. A new step-by-step plan to continue toward the original goal\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        return response.get('response', '')
