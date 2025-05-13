"""
Real Testing Script for Ultimate-AI

This script allows testing the Ultimate-AI system with real prompts.
It takes a prompt from the command line or stdin and runs it through
the system, showcasing the multi-model capabilities.
"""
import asyncio
import argparse
import sys

from core.plugins.apis.ollama_client import OllamaClient
from core.plugins.selenium_manager import SeleniumManager
from navigator.orchestrator import Navigator
from core.database.database import init_db

async def run_test_with_prompt(prompt, headless=False, verbose=False):
    """
    Run a test with the provided prompt.
    
    Args:
        prompt: The user's prompt/goal to execute
        headless: Whether to run browser in headless mode
        verbose: Whether to print detailed logs
    """
    print(f"Running test with prompt: {prompt}")
    
    # Initialize components
    ollama_client = OllamaClient()
    selenium_manager = SeleniumManager(headless=headless)
    navigator = Navigator(ollama_client, selenium_manager)
    
    try:
        # Initialize database
        init_db()
        
        if verbose:
            print("System initialized. Starting task execution...")
        
        # Execute the task based on the prompt
        await navigator.perform_web_goal(prompt)
        
        print("\n=== Task Summary ===")
        summary = await navigator.summarize_results(prompt)
        print(summary)
        
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        # Note: We don't need to explicitly close the browser here
        # as navigator.perform_web_goal() already handles this in its finally block
        print("Test completed.")

def main():
    """Main entry point for the real testing script."""
    parser = argparse.ArgumentParser(description="Run real tests with Ultimate-AI")
    parser.add_argument("--prompt", "-p", help="Prompt to test (if not provided, will read from stdin)")
    parser.add_argument("--headless", "-H", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Get prompt from args or stdin
    if args.prompt:
        prompt = args.prompt
    else:
        print("Enter your prompt (Ctrl+D or Ctrl+Z to end):")
        prompt = sys.stdin.read().strip()
    
    if not prompt:
        print("Error: Empty prompt. Please provide a prompt to test.")
        return
    
    # Run the test
    asyncio.run(run_test_with_prompt(prompt, args.headless, args.verbose))

if __name__ == "__main__":
    main() 