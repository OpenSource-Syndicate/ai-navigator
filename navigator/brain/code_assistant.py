# Code Assistant: Uses Granite-Code LLM for code generation and automation logic.
from typing import Dict, Any, Optional, List
from rich.console import Console
import json

console = Console()

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
        # Handle None values
        if page_content is None:
            page_content = ""
        if previous_actions is None:
            previous_actions = []
            
        previous_actions_text = "\n".join(previous_actions) if previous_actions else "No previous actions"
        
        # Limit page content to avoid token overflow
        page_content_sample = page_content[:3000] + "..." if len(page_content) > 3000 else page_content
        
        prompt = (
            "You are Granite-Code, an expert AI assistant specializing in writing Selenium automation scripts in Python. "
            "Generate Python code using Selenium to accomplish the following task:\\n\\n"
            f"GOAL: {goal}\\n\\n"
            f"CURRENT URL: {current_url}\\n\\n"
            f"PREVIOUS ACTIONS:\\n{previous_actions_text}\\n\\n"
            f"PAGE CONTENT SAMPLE (first 3000 chars):\\n{page_content_sample}\\n\\n"
            "Important requirements:\\n"
            "1. Use reliable selectors (prefer IDs, then CSS selectors, XPath as last resort).\\n"
            "2. Include explicit waits (WebDriverWait) for elements to be present or clickable before interacting. DO NOT use implicit waits or time.sleep().\\n"
            "3. Return ONLY executable Python code. Do not include any explanations, comments, introductory text, or markdown formatting like ```python. Just the raw code.\\n"
            "4. Assume the WebDriver instance is already created and available in a variable named `driver`.\\n"
            "5. Ensure the generated code snippet is complete and can run independently within an environment where `driver` exists.\\n"
            "6. Import necessary Selenium modules (e.g., By, Keys, WebDriverWait, expected_conditions as EC).\\n"
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        console.print(f"[magenta]Code Assistant generated Selenium code. Goal: {goal}[/magenta]")
        console.print(f"[dim]Prompt:\n{prompt}[/dim]")
        console.print(f"[dim]Response:\n{response.get('response', '')}[/dim]")
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
            "You are Granite-Code, an expert AI assistant specializing in debugging Python code. "
            "Fix the following Python code snippet that produced an error:\\n\\n"
            f"CODE WITH ERROR:\\n```python\\n{code}\\n```\\n\\n"
            f"ERROR MESSAGE: {error_message or 'No error message provided.'}\\n\\n"
            "Return ONLY the fixed, complete Python code snippet. Do not include explanations or markdown formatting."
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        console.print(f"[magenta]Code Assistant attempting to fix code.[/magenta]")
        console.print(f"[dim]Prompt:\n{prompt}[/dim]")
        console.print(f"[dim]Response:\n{response.get('response', '')}[/dim]")
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
            f"You are Granite-Code, an expert AI assistant specializing in writing Python code to interact with APIs. "
            f"Generate Python code using the `{use_library}` library to replay this API request:\\n\\n"
            f"REQUEST DETAILS:\\n```json\\n{json.dumps(request_data, indent=2)}\\n```\\n\\n"
            "The generated code should:\\n"
            "1. Include all necessary imports for the `{use_library}` library.\\n"
            "2. Accurately reproduce the request method, URL, headers, and body/payload.\\n"
            "3. Include basic handling for the response (e.g., print status code and response body).\\n"
            "4. Be well-structured and easy to understand.\\n"
            f"Return ONLY executable Python code for the `{use_library}` library. Do not include explanations or markdown formatting."
        )
        
        response = await self.ollama_client.generate_text(prompt, model_type="coding")
        console.print(f"[magenta]Code Assistant generating API replay code.[/magenta]")
        console.print(f"[dim]Prompt:\n{prompt}[/dim]")
        console.print(f"[dim]Response:\n{response.get('response', '')}[/dim]")
        return response.get('response', '')
