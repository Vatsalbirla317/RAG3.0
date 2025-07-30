from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum

# Enums
class RepositoryStatus(str, Enum):
    IDLE = "idle"
    CLONING = "cloning"
    INDEXING = "indexing"
    READY = "ready"
    ERROR = "error"

class SecuritySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

# Base Models
class Repository(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    url: HttpUrl
    path: str
    clonedAt: Optional[datetime] = None
    status: Optional[RepositoryStatus] = None

class CodeSnippet(BaseModel):
    id: str
    content: str
    code: str
    language: str
    filename: str
    filePath: str
    lineNumbers: Optional[bool] = None

class Message(BaseModel):
    id: str
    content: str
    role: MessageRole
    timestamp: datetime
    codeSnippets: Optional[List[CodeSnippet]] = None

class SecurityIssue(BaseModel):
    type: str
    severity: SecuritySeverity
    description: str
    line: int
    recommendation: str

# Request Models
class CloneRequest(BaseModel):
    repo_url: HttpUrl

class ChatRequest(BaseModel):
    question: str
    top_k: int = 5

class ExplainRequest(BaseModel):
    code: str
    complexity: str  # "5-year-old", "10-year-old", "teenager", "adult"

class SecurityScanRequest(BaseModel):
    file_path: str

class VisualizeRequest(BaseModel):
    codebase_path: str

class PreviewRequest(BaseModel):
    html: str
    css: str
    js: str

# Response Models
class CloneResponse(BaseModel):
    success: bool
    message: str
    repo_path: str

class StatusResponse(BaseModel):
    status: str
    message: str
    progress: float  # 0.0-1.0

class ChatResponse(BaseModel):
    answer: str
    retrieved_code: Optional[List[str]] = None

class ExplanationResponse(BaseModel):
    explanation: str

class SecurityScanResponse(BaseModel):
    issues: List[SecurityIssue]
    risk_level: str

class VisualizationResponse(BaseModel):
    graph_data: Any

class PreviewResponse(BaseModel):
    preview_url: str

class RepoInfoResponse(BaseModel):
    repo_name: str
    repo_description: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_keys_configured: dict 