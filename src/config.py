"""Configuration management for Azure Search and OpenAI."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure Search Configuration
    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index_name: str

    # Azure OpenAI Configuration
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_deployment_name: str
    azure_openai_api_version: str = "2023-05-15"

    # API Configuration
    max_tokens: int = 1000
    temperature: float = 0.7

    class Config:
        """Config for settings."""
        # Use absolute path to .env file
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False


try:
    settings = Settings()
    print(f"✓ Settings loaded successfully from {Settings.Config.env_file}")
    print(f"  - Azure Search: {settings.azure_search_endpoint}")
    print(f"  - Azure OpenAI: {settings.azure_openai_endpoint}")
    print(f"  - Deployment: {settings.azure_openai_deployment_name}")
except Exception as e:
    print(f"✗ Failed to load settings: {e}")
    raise
