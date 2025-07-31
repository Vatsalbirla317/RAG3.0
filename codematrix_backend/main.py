from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List
from contextlib import asynccontextmanager

# Import our modules
from models.schemas import *
from core.config import settings
from core.ai_service import ai_service
from core.state_manager import get_state, update_state, reset_state, app_state
from core.cloning_service import clone_and_process_repo
from core.rag_service import query_codebase, get_vector_db, clear_all_vector_dbs, get_vector_store_info

# Load environment variables
load_dotenv()

# --- Startup Logic ---
def rehydrate_state_on_startup():
    """
    Initialize the application state on startup.
    Since we're using in-memory storage, we start with a clean state.
    """
    print("Application starting up with in-memory storage...")
    # Start with a clean idle state since we can't persist vector databases
    app_state.update({
        "status": "idle",
        "message": "Ready to process repositories.",
        "progress": 0.0,
        "repo_path": "",
        "repo_name": "",
        "is_processing": False
    })
    # Clear all vector stores on startup
    clear_all_vector_dbs()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    rehydrate_state_on_startup()
    yield
    # Shutdown
    print("Application shutting down...")

app = FastAPI(
    title="CodeMatrix Backend", 
    version="1.0.0",
    description="AI-powered code analysis and chat platform",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:8080",
        "https://rag-3-0-nine.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all for now, restrict later
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
    Clones a GitHub repository and processes it for AI analysis.
    """
    try:
        # Check if already processing
        current_state = await get_state()
        if current_state.get("is_processing", False):
            raise HTTPException(status_code=409, detail="Another repository is currently being processed. Please wait.")

        # Clear ALL vector stores before processing new repository
        print("Clearing all vector stores before processing new repository...")
        clear_all_vector_dbs()

        # Start the background task
        background_tasks.add_task(clone_and_process_repo, request.repo_url)
        
        return CloneResponse(
            success=True,
            message="Repository cloning started. Check /status for progress.",
            repo_path=""
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in clone endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=StatusResponse, tags=["Repository"])
async def get_status():
    """
    Returns the current status of repository processing.
    """
    state = await get_state()
    return StatusResponse(
        status=state.get("status", "idle"),
        message=state.get("message", "No repository loaded"),
        progress=state.get("progress", 0.0)
    )

@app.post("/debug/reset")
async def reset_application_state():
    """
    Resets the application state (for debugging).
    """
    await reset_state()
    clear_all_vector_dbs()
    return {"message": "Application state reset successfully"}

@app.get("/debug/state")
async def debug_state():
    """
    Returns the full application state for debugging.
    """
    state = await get_state()
    vector_info = get_vector_store_info()
    return {
        **state,
        "vector_stores": vector_info,
        "vector_db_exists": get_vector_db(state.get('repo_name', '')) is not None if state.get("repo_name") else False
    }

@app.get("/debug/vector-stores")
async def debug_vector_stores():
    """
    Returns information about current vector stores in memory.
    """
    return get_vector_store_info()

@app.get("/repo_info", response_model=RepoInfoResponse)
async def get_repo_info():
    """
    Returns information about the currently loaded repository.
    """
    state = await get_state()
    repo_name = state.get("repo_name", "")
    
    if not repo_name:
        raise HTTPException(status_code=404, detail="No repository currently loaded")
    
    return RepoInfoResponse(
        repo_name=repo_name,
        repo_description="Repository loaded and indexed in memory"
    )

@app.post("/chat", response_model=ChatResponse, tags=["AI"])
async def chat_with_repo(request: ChatRequest):
    """
    Chat with the AI about the loaded codebase.
    """
    try:
        result = await query_codebase(request.question, request.top_k)
        return ChatResponse(
            answer=result["answer"],
            retrieved_code=result.get("retrieved_code", [])
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain", response_model=ExplanationResponse)
async def explain_code(request: ExplainRequest):
    """
    Explain code in different complexity levels.
    """
    try:
        # Create a prompt for explanation
        prompt = f"""
        Explain the following code like I'm a {request.complexity}:
        
        {request.code}
        
        Provide a clear, {request.complexity}-friendly explanation with examples if helpful.
        """
        
        response = await ai_service.chat(prompt)
        return ExplanationResponse(explanation=response)
    except Exception as e:
        print(f"Error in explain endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security-scan", response_model=SecurityScanResponse)
async def security_scan(request: SecurityScanRequest):
    """
    Scan code for security vulnerabilities.
    """
    try:
        # Create a security analysis prompt
        prompt = f"""
        Analyze the following code for security vulnerabilities:
        
        File: {request.file_path}
        Code:
        {request.code}
        
        Provide a detailed security analysis including:
        1. Potential vulnerabilities
        2. Severity levels (low/medium/high/critical)
        3. Specific recommendations for fixes
        4. Line numbers where issues are found
        
        Format your response as a structured analysis.
        """
        
        response = await ai_service.chat(prompt)
        
        # For now, return a mock response structure
        # In a real implementation, you'd parse the AI response into structured data
        return SecurityScanResponse(
            issues=[
                {
                    "type": "Security Analysis",
                    "severity": "medium",
                    "description": "AI analysis completed",
                    "line": 1,
                    "recommendation": "Review the AI analysis above for specific recommendations"
                }
            ],
            risk_level="medium"
        )
    except Exception as e:
        print(f"Error in security scan endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize", response_model=VisualizationResponse)
async def visualize_code(request: VisualizeRequest):
    """
    Generate visualizations for code structure.
    """
    try:
        # Create a visualization prompt
        prompt = f"""
        Create a visualization description for the codebase at: {request.codebase_path}
        
        Generate a detailed description of how to visualize:
        1. File structure and relationships
        2. Code dependencies
        3. Function call graphs
        4. Data flow diagrams
        
        Provide this in a format that can be used to create visual diagrams.
        """
        
        response = await ai_service.chat(prompt)
        
        return VisualizationResponse(
            graph_data={
                "description": response,
                "type": "codebase_visualization",
                "generated_at": datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Error in visualize endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preview", response_model=PreviewResponse)
async def preview_code(request: PreviewRequest):
    """
    Generate a live preview URL for HTML/CSS/JS code.
    """
    try:
        # In a real implementation, you'd save the code to a temporary file
        # and serve it via a preview service
        preview_url = f"data:text/html;base64,{request.html.encode('utf-8').hex()}"
        
        return PreviewResponse(preview_url=preview_url)
    except Exception as e:
        print(f"Error in preview endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT) 