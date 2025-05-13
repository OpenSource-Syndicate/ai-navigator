# Task Planner: Uses Hermes-3 LLM for high-level planning and reasoning.
from typing import List, Dict, Any, Optional
from rich.console import Console

console = Console()

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
            "You are Hermes-3, an expert AI assistant specializing in web automation planning. "
            "Your task is to create a precise and actionable step-by-step plan to achieve the given web automation goal. "
            "The steps in your plan will be executed using Python and the Selenium library to control a web browser. "
            "Consider the current state of the browser and any past API interactions to inform your plan.\\n\\n"
            f"GOAL: {user_goal}\\n\\n"
            f"CURRENT STATE:\\n- URL: {current_url or 'No current URL'}\\n- Page content sample (first 1500 chars): {page_content_sample}\\n"
            f"{api_history_str}\\n\\n"
            "Your plan should:\\n"
            "1. Break down the goal into small, clear, and individually executable steps (e.g., 'Navigate to URL', 'Type text into input field with name X', 'Click button with text Y').\\n"
            "2. For each step, identify the specific UI elements to interact with (e.g., by name, ID, text, or CSS selector if obvious from page content sample).\\n"
            "3. Anticipate potential challenges (e.g., element not found, unexpected pop-up) and briefly suggest fallback approaches or checks.\\n"
            "4. Ensure the plan follows the most efficient path to the goal.\\n"
            "5. Structure your response STRICTLY as a numbered list of steps. Do not include any preamble or a-conclusion.\\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        console.print(f"DEBUG: Raw response from planner model: [yellow]{response}[/yellow]")
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
            "You are Hermes-3, an expert AI assistant specializing in web page analysis. "
            "Analyze the provided webpage UI content and identify key interactive elements and their purpose.\\n\\n"
            f"URL: {current_url or 'No URL provided'}\\n\\n"
            f"PAGE CONTENT (first 3000 chars):\\n{page_content_sample}\\n\\n"
            "Provide a structured analysis that includes:\\n"
            "1. The main purpose or objective of this page (e.g., 'Login form', 'Product search results', 'Article display').\\n"
            "2. Key interactive elements (e.g., buttons, forms, input fields, links) and their likely functions. Be specific (e.g., 'Button with text \\'Submit\\'', 'Input field with name \\'username\\'').\\n"
            "3. Main navigation options available on the page (e.g., 'Header navigation links: Home, About, Contact', 'Sidebar menu with categories').\\n"
            "4. Any apparent authentication requirements or input forms (e.g., 'Login form with username and password fields', 'Search bar').\\n"
            "5. A brief summary of the overall page structure or layout.\\n"
            "Respond ONLY with the structured analysis, starting with point 1."
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
            "You are Hermes-3, an expert AI assistant specializing in troubleshooting web automation errors. "
            "An error occurred during a web automation task that uses Python and Selenium. Help create a recovery plan.\\n\\n"
            f"ORIGINAL GOAL: {original_goal}\\n\\n"
            f"STEPS COMPLETED BEFORE ERROR:\\n{steps_completed_str or 'No steps were completed.'}\\n\\n"
            f"ERROR CONTEXT: {error_context}\\n\\n"
            "Please provide a concise recovery strategy focusing on:\\n"
            "1. A brief analysis of what likely went wrong based on the error and context (consider Selenium-specific issues like element locators, waits, or page changes).\\n"
            "2. One or two practical alternate approaches to try using Selenium, or how to adjust the failed Selenium step.\\n"
            "3. A new, short, step-by-step plan (max 3-4 steps) using Selenium actions to continue towards the original goal, starting from the point of recovery. "
            "If the goal seems unachievable with the current error, suggest a revised, achievable sub-goal.\\n"
            "Structure your response clearly with these three numbered points."
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="general")
        return response.get('response', '')
