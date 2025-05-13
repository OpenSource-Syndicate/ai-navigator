import asyncio
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl

from core.database.database import get_db, init_db
from core.database.models import LearnedInfo, APIRequest
from core.plugins.apis.ollama_client import OllamaClient
from core.plugins.selenium_manager import SeleniumManager
from navigator.orchestrator import Navigator

app = FastAPI(title="Ultimate AI - Web Navigator")

# Initialize components
ollama_client = OllamaClient()
selenium_manager = SeleniumManager(headless=False)  # Set to True in production
navigator = Navigator(ollama_client, selenium_manager)

# Initialize the database on startup
@app.on_event("startup")
def startup_db_client():
    init_db()

# Request and response models
class WebGoalRequest(BaseModel):
    goal: str
    context: Optional[str] = None
    run_headless: Optional[bool] = False

class WebCaptureRequest(BaseModel):
    url: HttpUrl
    context: Optional[str] = None

class ApiSearchRequest(BaseModel):
    query: str

class SemanticSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class CodeGenerationRequest(BaseModel):
    task: str
    language: Optional[str] = "python"

class GenerateResponse(BaseModel):
    content: str
    source: Optional[str] = None

class ApiListResponse(BaseModel):
    apis: List[Dict[str, Any]]

@app.post("/navigate", response_model=Dict[str, str])
async def navigate_web(request: WebGoalRequest, background_tasks: BackgroundTasks):
    """
    Start a web navigation session with the specified goal.
    
    This endpoint demonstrates the multi-model orchestration:
    1. Hermes-3 creates a plan
    2. Granite-Code generates the execution code
    3. As actions are taken, requests are captured
    4. DeepSeek-R1 analyzes the API interactions
    5. mxbai-embed stores and connects the semantic knowledge
    """
    # Set headless mode if requested
    if hasattr(navigator.selenium_manager, 'headless'):
        navigator.selenium_manager.headless = request.run_headless
    
    # Start the navigation in the background
    background_tasks.add_task(
        navigator.perform_web_goal,
        request.goal
    )
    
    return {
        "status": "Navigation started in background",
        "goal": request.goal
    }

@app.post("/plan", response_model=Dict[str, str]) 
async def get_plan(request: WebGoalRequest):
    """Get just the initial plan for a goal without executing it."""
    plan = await navigator.handle_user_request(request.goal, request.context or "")
    return {"plan": plan}

@app.post("/analyze-webpage", response_model=GenerateResponse)
async def analyze_webpage(request: WebCaptureRequest, db: Session = Depends(get_db)):
    """Analyze a webpage using the AI models."""
    # Extract content from webpage
    if not hasattr(selenium_manager, 'extract_page_content'):
        # Create a simple method if it doesn't exist
        selenium_manager.driver.get(str(request.url))
        page_content = {
            'title': selenium_manager.driver.title,
            'content': selenium_manager.driver.page_source
        }
    else:
        page_content = await selenium_manager.extract_page_content(str(request.url))
    
    # Use our TaskPlanner (Hermes-3) to analyze the page
    analysis = await navigator.planner.analyze_ui(
        page_content.get('content', ''),
        current_url=str(request.url)
    )
    
    # Store the learned information
    learned_info = LearnedInfo(
        topic=page_content.get('title', 'Webpage Analysis'),
        content=analysis.get('full_analysis', ''),
        source=str(request.url)
    )
    db.add(learned_info)
    db.commit()
    
    return GenerateResponse(
        content=analysis.get('full_analysis', ''),
        source=str(request.url)
    )

@app.post("/apis/search", response_model=ApiListResponse)
async def search_apis(request: ApiSearchRequest):
    """Search for captured APIs matching a query."""
    api_memories = await navigator.api_search(request.query)
    
    # Format for response
    results = []
    for api in api_memories:
        results.append({
            "id": api.get("id", ""),
            "text": api.get("text", ""),
            "similarity": api.get("similarity_score", 0),
            "metadata": api.get("metadata", {})
        })
    
    return ApiListResponse(apis=results)

@app.post("/generate/code", response_model=Dict[str, str])
async def generate_code(request: CodeGenerationRequest):
    """Generate code for a specific task using Granite-Code."""
    code = await navigator.generate_code_for_task(request.task)
    return {"code": code}

@app.get("/apis/recent", response_model=ApiListResponse)
async def get_recent_apis(limit: int = 10, db: Session = Depends(get_db)):
    """Get recently captured API requests."""
    api_requests = db.query(APIRequest).order_by(APIRequest.timestamp.desc()).limit(limit).all()
    
    # Format for response
    results = []
    for api in api_requests:
        results.append({
            "id": api.id,
            "method": api.method,
            "url": api.url,
            "response_status": api.response_status_code,
            "notes": api.notes
        })
    
    return ApiListResponse(apis=results)

@app.post("/memory/search", response_model=Dict[str, Any])
async def search_semantic_memory(request: SemanticSearchRequest):
    """Search the semantic memory using mxbai embeddings."""
    results = await navigator.semantic_indexer.search_memory(request.query, top_k=request.top_k)
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
