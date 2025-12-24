"""
Configuration settings for the Agentic AI system
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Project Settings
    PROJECT_NAME: str = "Doxa Agentic AI"
    API_V1_STR: str = "/api/v1"
    
    # AI/RAG Settings (use .env file or environment variables - NEVER hardcode!)
    GEMINI_API_KEY: str = ""  # Set via .env or GEMINI_API_KEY env var
    MISTRAL_API_KEY: str = ""  # Set via .env or MISTRAL_API_KEY env var
    
    # BGE Model Settings
    BGE_MODEL_NAME: str = "BAAI/bge-m3"
    BGE_USE_FP16: bool = True
    BGE_MAX_LENGTH: int = 8192 
    
    # ChromaDB Settings
    CHROMA_PERSIST_PATH: str = "data/chroma_archive"
    CHROMA_COLLECTION_NAME: str = "test_collection"
    CHROMA_N_RESULTS: int = 2
    
    # Data Paths
    DATA_DIR: str = "data"
    EMBEDDINGS_DIR: str = "data/embeddings"
    RAW_DOCS_DIR: str = "data/raw_docs"
    
    # Gemini Settings
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_MAX_OUTPUT_TOKENS: int = 100000
    GEMINI_TEMPERATURE: float = 0.0
    
    # Mistral Settings
    MISTRAL_MODEL_ID: str = "mistral-small-latest"
    MISTRAL_TEMPERATURE: float = 0.1
    
    # Backend Integration
    BACKEND_API_URL: str = "http://localhost:8000"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]


settings = Settings()
