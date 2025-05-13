# Code Assistant: Uses Granite-Code LLM for code generation and automation logic.
from typing import Dict, Any, Optional, List

class CodeAssistant:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client

    async def generate_code(self, prompt: str) -> str:
        """Generate code based on a given prompt."""
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        return response.get('response', '')
    
    async def generate_selenium_code(self, 
                                   goal: str, 
                                   current_url: str = "", 
                                   page_content: str = "", 
                                   previous_actions: List[str] = None) -> str:
        """
        Generate Selenium/Playwright code for web automation based on a specific goal.
        
        Args:
            goal: What needs to be accomplished (e.g., "Click the login button")
            current_url: The URL of the current page
            page_content: HTML content or summary of current page
            previous_actions: List of previously performed actions
            
        Returns:
            Python code that can be executed to achieve the goal
        """
        previous_actions_text = "\n".join(previous_actions) if previous_actions else "No previous actions"
        
        # Limit page content to avoid token overflow
        page_content_sample = page_content[:3000] + "..." if len(page_content) > 3000 else page_content
        
        prompt = (
            "Generate Python code using Selenium to accomplish the following task:\n\n"
            f"GOAL: {goal}\n\n"
            f"CURRENT URL: {current_url}\n\n"
            f"PREVIOUS ACTIONS:\n{previous_actions_text}\n\n"
            f"PAGE CONTENT SAMPLE:\n{page_content_sample}\n\n"
            "Important requirements:\n"
            "1. Use reliable selectors (prefer IDs, then CSS selectors, XPath as last resort)\n"
            "2. Include proper waits and error handling\n"
            "3. Return only executable Python code without explanations\n"
            "4. Use driver as the WebDriver variable name\n"
            "5. Ensure the code is complete and can run independently\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        return response.get('response', '')
    
    async def fix_code(self, code: str, error_message: str = "") -> str:
        """
        Fix broken code based on an error message.
        
        Args:
            code: The code that needs fixing
            error_message: The error message received, if any
            
        Returns:
            Fixed code
        """
        prompt = (
            "Fix the following Python code that has an error:\n\n"
            f"CODE:\n```python\n{code}\n```\n\n"
            f"ERROR MESSAGE: {error_message}\n\n"
            "Return only the fixed code without explanations."
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        return response.get('response', '')
    
    async def generate_api_replay_code(self, 
                                     request_data: Dict[str, Any], 
                                     use_library: str = "requests") -> str:
        """
        Generate code to replay an API request.
        
        Args:
            request_data: Dictionary containing request details
            use_library: Library to use (requests, httpx, aiohttp, etc.)
            
        Returns:
            Code that replays the API request
        """
        prompt = (
            f"Generate Python code using the {use_library} library to replay this API request:\n\n"
            f"```\n{request_data}\n```\n\n"
            "The code should:\n"
            "1. Include all necessary imports\n"
            "2. Preserve all headers and parameters exactly\n"
            "3. Handle the response appropriately\n"
            "4. Be well-structured and maintainable\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        return response.get('response', '')
