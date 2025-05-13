# navigator/web_navigator.py

import asyncio
import json
import traceback
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from core.plugins.selenium_manager import SeleniumManager
from core.database.models import APIRequest
from core.database.database import get_db # Assuming get_db is accessible

from navigator.brain.code_assistant import CodeAssistant
from navigator.brain.planner import TaskPlanner
from navigator.brain.api_reverse_engineer import APIReverseEngineer
from navigator.memory.semantic_indexer import SemanticIndexer
from core.plugins.apis.ollama_client import OllamaClient

class WebNavigator:
    def __init__(
        self, 
        ollama_client: 'OllamaClient', 
        selenium_manager: SeleniumManager,
        db_session_factory = get_db # Allow injecting db session factory for testing
    ):
        self.ollama_client = ollama_client
        self.selenium_manager = selenium_manager
        self.db_session_factory = db_session_factory

        # Initialize brain components
        self.code_assistant = CodeAssistant(ollama_client)
        self.planner = TaskPlanner(ollama_client)
        self.api_reverse_engineer = APIReverseEngineer(ollama_client)
        self.semantic_indexer = SemanticIndexer(ollama_client)

        self.current_url: Optional[str] = None
        self.page_content: Optional[str] = None
        self.action_history: List[str] = []
        self.captured_apis: List[Dict[str, Any]] = []

    async def navigate_and_learn(self, user_goal: str):
        """Main loop for navigating, understanding, and learning from web interactions."""
        print(f"Starting navigation with goal: {user_goal}")

        try:
            # 1. Task Planning with Hermes-3
            plan = await self.planner.create_detailed_plan(
                user_goal=user_goal,
                current_url=self.current_url,
                page_content=self.page_content,
                api_history=self.captured_apis
            )
            print(f"Detailed Plan:\n{plan}")
            
            # Add plan to semantic memory
            await self.semantic_indexer.add_to_memory(
                item_id=f"plan_{len(self.action_history)}",
                text_content=f"Plan for goal: {user_goal}\n{plan}",
                metadata={"type": "plan", "goal": user_goal}
            )
            
            # 2. Parse the plan into steps (simplified implementation)
            plan_steps = [step.strip() for step in plan.split("\n") if step.strip()]
            
            # If plan is empty or doesn't have clear steps, implement a default behavior for common actions
            if not plan_steps:
                print("No clear plan steps detected. Implementing default behavior.")
                
                # Default behavior for search-related tasks
                if any(term in user_goal.lower() for term in ["search", "find", "look up", "google", "check"]):
                    print("Detected search intent. Implementing default search behavior.")
                    search_term = user_goal.lower().replace("search", "").replace("find", "").replace("look up", "").replace("google", "").replace("check", "").strip()
                    
                    # Go to Google
                    await self.go_to_url("https://www.google.com")
                    
                    # Try to search
                    if self.selenium_manager.driver:
                        try:
                            # Generate search code
                            search_code = """
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "q"))
)
search_input.clear()
search_input.send_keys(f"{search_term}")
search_input.send_keys(Keys.RETURN)
                            """.replace("{search_term}", search_term)
                            
                            await self.execute_selenium_code(search_code)
                            self.action_history.append(f"DEFAULT: Searched for '{search_term}' on Google")
                            return
                        except Exception as e:
                            print(f"Error executing default search: {e}")
            
            # 3. Execute each step
            for i, step in enumerate(plan_steps):
                print(f"Executing step {i+1}: {step}")
                
                # Record the step we're attempting
                self.action_history.append(f"PLAN STEP: {step}")
                
                # Check if this step is a navigation step
                if "navigate" in step.lower() or "go to" in step.lower() or "open" in step.lower():
                    # Extract URL (simplified)
                    url_parts = step.split(" ")
                    for part in url_parts:
                        if part.startswith("http") or "www." in part:
                            await self.go_to_url(part)
                            break
                    # If no URL found, try to generate code for this step
                    if self.current_url is None:
                        await self.execute_step_with_code_generation(step)
                else:
                    # Use CodeAssistant to generate code for this step
                    await self.execute_step_with_code_generation(step)
                
                # After each step, pause to simulate realistic interaction
                # and to give time for the page to load/APIs to fire
                await asyncio.sleep(1)
                
                # After each step, analyze current page (if we're on a page)
                if self.page_content:
                    # Use Hermes to analyze the UI
                    ui_analysis = await self.planner.analyze_ui(
                        page_content=self.page_content,
                        current_url=self.current_url
                    )
                    # Save UI analysis to semantic memory
                    await self.semantic_indexer.add_to_memory(
                        item_id=f"ui_analysis_{len(self.action_history)}",
                        text_content=ui_analysis.get("full_analysis", ""),
                        metadata={
                            "type": "ui_analysis", 
                            "url": self.current_url,
                            "step": step
                        }
                    )
            
            print("Navigation and learning process complete.")
            
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"Error during navigation: {e}\n{error_trace}")
            
            # Use Hermes to generate recovery plan
            recovery_plan = await self.planner.handle_error(
                error_context=str(e),
                original_goal=user_goal,
                steps_completed=self.action_history
            )
            print(f"Recovery Plan:\n{recovery_plan}")
            
            # Implement a simple default behavior for common goals if we've encountered an error
            if any(term in user_goal.lower() for term in ["search", "find", "look up", "google", "check"]):
                print("Error occurred. Trying direct search as fallback.")
                search_term = user_goal.lower().replace("search", "").replace("find", "").replace("look up", "").replace("google", "").replace("check", "").strip()
                search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                await self.go_to_url(search_url)

    async def execute_step_with_code_generation(self, step_description: str):
        """Generate and execute code for a specific step."""
        # Generate code with Granite-Code
        selenium_code = await self.code_assistant.generate_selenium_code(
            goal=step_description,
            current_url=self.current_url,
            page_content=self.page_content,
            previous_actions=self.action_history[-5:] if len(self.action_history) > 5 else self.action_history
        )
        
        # Add to action history
        self.action_history.append(f"GENERATED CODE: {selenium_code[:100]}...")
        
        # Execute the code
        try:
            await self.execute_selenium_code(selenium_code)
        except Exception as e:
            print(f"Error executing generated code: {e}")
            # Try to fix the code
            fixed_code = await self.code_assistant.fix_code(
                code=selenium_code,
                error_message=str(e)
            )
            self.action_history.append(f"FIXED CODE: {fixed_code[:100]}...")
            
            # Try again with fixed code
            try:
                await self.execute_selenium_code(fixed_code)
            except Exception as e2:
                print(f"Error executing fixed code: {e2}")
                # Record the failure
                self.action_history.append(f"CODE EXECUTION FAILED: {str(e2)}")

    async def go_to_url(self, url: str):
        """Navigates to a given URL using Selenium."""
        print(f"Navigating to: {url}")
        try:
            # Make sure driver is created before use
            if not hasattr(self.selenium_manager, 'driver') or self.selenium_manager.driver is None:
                self.selenium_manager.create_driver()
                
            self.selenium_manager.driver.get(url)
            self.current_url = self.selenium_manager.driver.current_url
            self.page_content = self.selenium_manager.driver.page_source # Basic page content
            # Add to semantic memory
            await self.semantic_indexer.add_to_memory(
                item_id=f"page_{self.current_url}", 
                text_content=f"Visited page: {self.current_url}\nPage Title: {self.selenium_manager.driver.title}\nFirst 500 chars: {self.page_content[:500]}",
                metadata={"url": self.current_url, "type": "webpage_visit"}
            )
            self.action_history.append(f"NAVIGATION: Went to {self.current_url}")
            print(f"Successfully navigated to: {self.current_url}")
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            self.action_history.append(f"NAVIGATION ERROR: {str(e)}")

    async def process_and_store_api_request(self, request_data: Dict[str, Any], response_data: Optional[Dict[str, Any]] = None):
        """
        Analyzes a captured API request using APIReverseEngineer, 
        stores it in the database, and adds it to semantic memory.
        """
        print(f"Processing API request: {request_data.get('method')} {request_data.get('url')}")

        # 1. Add to captured APIs list for future reference
        self.captured_apis.append(request_data)

        # 2. Analyze with APIReverseEngineer (using the enhanced method)
        analysis = await self.api_reverse_engineer.analyze_request_response_pair(request_data, response_data)
        print(f"API Analysis:\n{analysis}")

        # 3. Store in Database
        db: Session = next(self.db_session_factory())
        try:
            db_request = APIRequest(
                method=request_data.get("method"),
                url=request_data.get("url"),
                headers=json.dumps(request_data.get("headers")),
                body=json.dumps(request_data.get("body")),
                response_status_code=response_data.get("status_code") if response_data else None,
                response_body=json.dumps(response_data.get("body")) if response_data else None,
                notes=analysis
            )
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            print(f"API Request stored in DB with ID: {db_request.id}")
        except Exception as e:
            print(f"Error storing API request to DB: {e}")
            db.rollback()
        finally:
            db.close()

        # 4. Add to Semantic Memory
        semantic_id = f"api_{request_data.get('method')}_{request_data.get('url')}"
        semantic_text = f"API Request: {request_data.get('method')} {request_data.get('url')}\nHeaders: {request_data.get('headers')}\nBody: {request_data.get('body')}\nAnalysis: {analysis}"
        await self.semantic_indexer.add_to_memory(
            item_id=semantic_id,
            text_content=semantic_text,
            metadata={"type": "api_request", "url": request_data.get("url"), "method": request_data.get("method")}
        )
        print(f"API Request added to semantic memory with ID: {semantic_id}")
        
        # 5. Add to action history
        self.action_history.append(f"API CAPTURED: {request_data.get('method')} {request_data.get('url')}")
        
        # 6. Generate replay code (optional)
        replay_code = await self.code_assistant.generate_api_replay_code(request_data)
        await self.semantic_indexer.add_to_memory(
            item_id=f"{semantic_id}_replay",
            text_content=f"API Replay Code for {request_data.get('method')} {request_data.get('url')}:\n{replay_code}",
            metadata={"type": "api_replay_code", "url": request_data.get("url"), "method": request_data.get("method")}
        )

    async def generate_selenium_code(self, task_description: str) -> str:
        """Generates Selenium code for a given task using CodeAssistant."""
        # Context could include current page DOM, previous actions, etc.
        context = f"Current URL: {self.current_url}. Page source (first 1000 chars): {self.page_content[:1000] if self.page_content else 'N/A'}"
        prompt = f"Generate Python Selenium code to perform the following task on the current webpage:\n{task_description}\nContext: {context}"
        code = await self.code_assistant.generate_code(prompt)
        print(f"Generated Selenium code:\n{code}")
        return code

    async def execute_selenium_code(self, code_snippet: str):
        """Executes a snippet of Selenium Python code."""
        # DANGER: Executing arbitrary code is a security risk.
        # In a real system, this needs sandboxing and careful validation.
        print(f"Executing Selenium code (DANGER - UNSAFE):\n{code_snippet}")
        try:
            # Make sure driver is created before use
            if not hasattr(self.selenium_manager, 'driver') or self.selenium_manager.driver is None:
                self.selenium_manager.create_driver()
                
            # This is a simplified way to execute. A more robust solution would be needed.
            # It assumes 'driver' is available in the scope, which it is if self.selenium_manager.driver is used.
            # For safety, one might use a restricted exec environment or parse/validate the code.
            # For now, we'll assume the code uses `self.selenium_manager.driver`
            # A safer approach would be to have the LLM generate actions that are then translated to selenium calls by our code.
            
            # A very basic and unsafe way to make `driver` available to `exec`
            # This is NOT recommended for production.
            local_scope = {"driver": self.selenium_manager.driver, "self": self}
            exec(code_snippet, globals(), local_scope) 
            
            # Update current state after execution
            self.current_url = self.selenium_manager.driver.current_url
            self.page_content = self.selenium_manager.driver.page_source
            print("Selenium code executed successfully.")
            self.action_history.append("CODE EXECUTION: Success")
        except Exception as e:
            print(f"Error executing Selenium code: {e}")
            self.action_history.append(f"CODE EXECUTION ERROR: {str(e)}")
            raise

    def close_browser(self):
        """Close the browser session if it exists."""
        if hasattr(self, 'selenium_manager') and self.selenium_manager:
            self.selenium_manager.close_driver()
            print("Browser closed.")

# Example Usage (Illustrative - would be in main.py or a test script)
async def main_example():
    # This is a placeholder for OllamaClient initialization
    class MockOllamaClient:
        async def generate_text(self, prompt: str, model_type: str):
            print(f"MockOllamaClient.generate_text called with model_type: {model_type}")
            if model_type == "coding":
                return {"response": "print('Selenium code executed') # Placeholder code"}
            elif model_type == "reasoning":
                return {"response": "This API request seems to submit user data."}
            elif model_type == "general":
                return {"response": "Step 1: Go to example.com. Step 2: Click login."}
            elif model_type == "embedding":
                # Return a dummy embedding (list of floats)
                return {"embedding": [0.1] * 768} # Assuming 768 is embedding dim
            return {"response": ""}

    ollama_client_mock = MockOllamaClient()
    selenium_manager_instance = SeleniumManager(headless=True) # Or False to see browser
    
    navigator = WebNavigator(ollama_client_mock, selenium_manager_instance)

    try:
        await navigator.go_to_url("https://www.google.com") # Start somewhere
        # await navigator.navigate_and_learn("Find information about Python programming language and then search for images of cats.")
        
        # Simulate finding an API request
        sample_api_request = {
            "method": "GET",
            "url": "https://jsonplaceholder.typicode.com/todos/1",
            "headers": {"User-Agent": "UltimateAI-Navigator"},
            "body": None
        }
        sample_api_response = {
            "status_code": 200,
            "body": {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}
        }
        await navigator.process_and_store_api_request(sample_api_request, sample_api_response)

        # Test semantic search
        search_results = await navigator.semantic_indexer.search_memory("information about a specific task or item")
        print(f"Semantic search results: {search_results}")

        # Test code generation and execution
        # selenium_code = await navigator.generate_selenium_code("Type 'hello world' into the search bar and click the search button.")
        # if selenium_code:
        #     await navigator.execute_selenium_code(selenium_code)

    finally:
        navigator.close_browser()
        # Clean up database if it's a test DB

if __name__ == "__main__":
    # This example requires an active database (ultimate_ai.db) and tables created.
    # You would typically run init_db.py first.
    # asyncio.run(main_example())
    print("WebNavigator class defined. Run example usage from a main script or test.")