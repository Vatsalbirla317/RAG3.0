from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List

# Import our modules
from models.schemas import *
from core.config import settings
from core.ai_service import ai_service
from core.state_manager import get_state, update_state
from core.cloning_service import clone_and_process_repo

# Load environment variables
load_dotenv()

app = FastAPI(
    title="CodeMatrix Backend", 
    version="1.0.0",
    description="AI-powered code analysis and chat platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        api_keys_configured={
            "groq": settings.has_groq_key,
            "gemini_1": bool(settings.GEMINI_API_KEY_1),
            "gemini_2": bool(settings.GEMINI_API_KEY_2)
        }
    )

@app.post("/clone", response_model=CloneResponse, tags=["Repository"])
async def clone_repository(request: CloneRequest, background_tasks: BackgroundTasks):
    """
    Clones a public GitHub repository and starts the indexing process in the background.
    """
    # Start the background task
    background_tasks.add_task(clone_and_process_repo, str(request.repo_url))

    # Immediately return a response to the user
    return CloneResponse(
        success=True, 
        message="Repository cloning and indexing has started.",
        repo_path=""
    )

@app.get("/status", response_model=StatusResponse, tags=["Repository"])
async def get_status():
    """
    Returns the current status of the repository cloning/indexing process.
    """
    current_state = await get_state()
    return StatusResponse(**current_state)

@app.get("/repo_info", response_model=RepoInfoResponse)
async def get_repo_info():
    """Get current repository information"""
    current_state = await get_state()
    if current_state["status"] == "idle":
        raise HTTPException(status_code=404, detail="No repository loaded")
    
    return RepoInfoResponse(
        repo_name=current_state["repo_name"] or "Unknown",
        repo_description=current_state["repo_description"] or "No description available"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI about the codebase"""
    try:
        if not settings.has_any_ai_key:
            raise HTTPException(status_code=500, detail="No AI API keys configured")
        
        # For now, generate a simple response
        # In the full implementation, this would:
        # 1. Search the codebase for relevant code
        # 2. Use RAG to find context
        # 3. Generate AI response
        
        response = await ai_service.generate_chat_response(
            question=request.question,
            model=settings.DEFAULT_MODEL
        )
        
        # Mock retrieved code snippets
        retrieved_code = [
            "def example_function():\n    return 'Hello from CodeMatrix!'",
            "class ExampleClass:\n    def __init__(self):\n        self.name = 'CodeMatrix'"
        ]
        
        return ChatResponse(
            answer=response,
            retrieved_code=retrieved_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain", response_model=ExplanationResponse)
async def explain_code(request: ExplainRequest):
    """Explain code at different complexity levels"""
    try:
        if not settings.has_any_ai_key:
            raise HTTPException(status_code=500, detail="No AI API keys configured")
        
        explanation = await ai_service.explain_code(
            code=request.code,
            complexity=request.complexity,
            model=settings.DEFAULT_MODEL
        )
        
        return ExplanationResponse(explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security-scan", response_model=SecurityScanResponse)
async def security_scan(request: SecurityScanRequest):
    """Scan code for security vulnerabilities"""
    try:
        # Mock security scan results
        # In the full implementation, this would:
        # 1. Parse the code
        # 2. Run security analysis tools
        # 3. Return actual vulnerabilities
        
        issues = [
            SecurityIssue(
                type="SQL Injection",
                severity="high",
                description="Potential SQL injection vulnerability detected",
                line=15,
                recommendation="Use parameterized queries instead of string concatenation"
            )
        ]
        
        return SecurityScanResponse(
            issues=issues,
            risk_level="medium"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize", response_model=VisualizationResponse)
async def visualize_code(request: VisualizeRequest):
    """Generate code visualization"""
    try:
        # Mock visualization data
        # In the full implementation, this would:
        # 1. Parse the codebase
        # 2. Generate dependency graphs
        # 3. Return graph data
        
        graph_data = {
            "nodes": [
                {"id": "main.py", "type": "file"},
                {"id": "utils.py", "type": "file"}
            ],
            "edges": [
                {"from": "main.py", "to": "utils.py", "type": "import"}
            ]
        }
        
        return VisualizationResponse(graph_data=graph_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preview", response_model=PreviewResponse)
async def preview_code(request: PreviewRequest):
    """Generate live preview URL"""
    try:
        # Mock preview URL
        # In the full implementation, this would:
        # 1. Create a temporary file with the code
        # 2. Serve it via a web server
        # 3. Return the preview URL
        
        preview_url = f"http://localhost:8000/preview/{datetime.now().timestamp()}"
        
        return PreviewResponse(preview_url=preview_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT) 