# config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field
from typing import Dict, Any, Optional, List

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application Settings
    APP_NAME: str = os.getenv('APP_NAME', 'Budget Planner')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # API Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', 8000))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'budget_planner.log')
    
    # Feature Flags
    ENABLE_ADVANCED_CATEGORIZATION: bool = os.getenv('ENABLE_ADVANCED_CATEGORIZATION', 'true').lower() == 'true'
    ENABLE_SEASONAL_ANALYSIS: bool = os.getenv('ENABLE_SEASONAL_ANALYSIS', 'true').lower() == 'true'
    
    # Database settings
    DATABASE_URL: Optional[str] = Field(default=None)
    
    # LLM API settings
    LLM_PROVIDER: str = Field(default="anthropic")  # Options: anthropic, openai, perplexity, gemini
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    PERPLEXITY_API_KEY: Optional[str] = Field(default=None)
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    
    # LLM model settings
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229")
    OPENAI_MODEL: str = Field(default="gpt-4o")
    
    # Performance settings
    MAX_TOKENS: int = Field(default=4000)
    TEMPERATURE: float = Field(default=0.0)  # Lower for more deterministic responses
    
    # Security settings
    SECRET_KEY: str = Field(default="your-super-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000"])
    
    # Budget planning settings
    DEFAULT_CURRENCY: str = Field(default="USD")
    DEFAULT_SAVINGS_GOAL_PERCENTAGE: float = Field(default=20.0)
    CATEGORIES_FILE_PATH: str = Field(default="data/categories.json")
    TEMPLATE_FILE_PATH: str = Field(default="data/budget_templates.json")
    
    # File storage settings
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    
    # Caching settings
    CACHE_TTL: int = Field(default=3600)  # 1 hour
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_llm_api_key(self) -> Optional[str]:
        """Get the appropriate LLM API key based on the provider setting."""
        if self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_API_KEY
        elif self.LLM_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        elif self.LLM_PROVIDER == "perplexity":
            return self.PERPLEXITY_API_KEY
        elif self.LLM_PROVIDER == "gemini":
            return self.GEMINI_API_KEY
        return None
    
    def get_llm_model(self) -> str:
        """Get the appropriate LLM model based on the provider setting."""
        if self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_MODEL
        elif self.LLM_PROVIDER == "openai":
            return self.OPENAI_MODEL
        # Add more providers as needed
        return self.ANTHROPIC_MODEL  # Default fallback

# Create a singleton settings instance
settings = Settings()

# Make sure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
if settings.LOG_FILE:
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)