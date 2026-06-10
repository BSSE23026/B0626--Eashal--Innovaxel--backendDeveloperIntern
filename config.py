import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./event_registration.db"
    
    # API Configuration
    API_TITLE: str = "Event Registration System API"
    API_DESCRIPTION: str = "A REST API for managing event registrations with concurrent access safety"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()