import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the document parser service."""
    
    # Service settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "3006"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() in ("true", "1", "t")
    
    # Storage settings
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./data/documents")
    
    # Supported file formats
    SUPPORTED_FORMATS: List[str] = [".pdf", ".docx", ".jpg", ".jpeg", ".png"]
    
    # LlamaParser settings
    LLAMA_PARSER_API_KEY: str = os.getenv("LLAMA_PARSER_API_KEY", "")
    LLAMA_PARSER_API_URL: str = os.getenv("LLAMA_PARSER_API_URL", "https://api.llamaparser.ai")
    LLAMA_PARSER_TIMEOUT: int = int(os.getenv("LLAMA_PARSER_TIMEOUT", "60"))
    
    # OpenAI settings for fallback parsing
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    # Document extraction settings
    EXTRACTION_CONFIDENCE_THRESHOLD: float = float(os.getenv("EXTRACTION_CONFIDENCE_THRESHOLD", "0.7"))
    
    # Database settings (for a production implementation)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # AWS S3 settings (for production document storage)
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "harper-documents")
    
    # Metadata
    SERVICE_NAME: str = "document-parser"
    VERSION: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()

# Ensure storage path exists
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
