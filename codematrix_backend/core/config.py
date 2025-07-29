import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY_1: str = os.getenv("GEMINI_API_KEY_1", "")
    GEMINI_API_KEY_2: str = os.getenv("GEMINI_API_KEY_2", "")
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Repository Configuration
    REPO_STORAGE_PATH: str = os.getenv("REPO_STORAGE_PATH", "./repositories")
    MAX_REPO_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # AI Configuration
    DEFAULT_MODEL: str = "groq"  # "groq" or "gemini"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Security Configuration
    ALLOWED_FILE_EXTENSIONS: list = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", 
        ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @property
    def has_groq_key(self) -> bool:
        return bool(self.GROQ_API_KEY)
    
    @property
    def has_gemini_keys(self) -> bool:
        return bool(self.GEMINI_API_KEY_1 or self.GEMINI_API_KEY_2)
    
    @property
    def has_any_ai_key(self) -> bool:
        return self.has_groq_key or self.has_gemini_keys

# Global settings instance
settings = Settings() 