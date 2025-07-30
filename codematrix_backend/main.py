from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List

# Import our modules
from models.schemas import *
from core.config import settings
from core.ai_service import ai_service
from core.state_manager import get_state, update_state, reset_state
from core.cloning_service import clone_and_process_repo
from core.rag_service import query_codebase

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
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/", include_in_schema=False)
async def root():
    """
    Redirects the root URL to the API documentation.
    """
    return RedirectResponse(url="/docs")

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

@app.post("/debug/reset")
async def reset_application_state():
    """Reset the application state (for debugging)"""
    await reset_state()
    return {"message": "State reset successfully"}

@app.get("/debug/state")
async def debug_state():
    """Get detailed state information for debugging"""
    import os
    state = await get_state()
    return {
        "state": state,
        "has_repo": bool(state.get("repo_name")),
        "repo_path_exists": os.path.exists(state.get("repo_path", "")) if state.get("repo_path") else False,
        "vector_db_exists": os.path.exists(f"vector_db/{state.get('repo_name', '')}") if state.get("repo_name") else False
    }

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

@app.post("/chat", response_model=ChatResponse, tags=["AI"])
async def chat_with_repo(request: ChatRequest):
    """
    Handles chat queries against the indexed repository using a RAG pipeline.
    """
    try:
        if not settings.has_any_ai_key:
            raise HTTPException(status_code=500, detail="No AI API keys configured")
        
        # Use the RAG service to query the codebase
        response = await query_codebase(request.question, request.top_k)
        
        return ChatResponse(
            answer=response["answer"],
            retrieved_code=response["retrieved_code"]
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