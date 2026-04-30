"""Pydantic settings; .env locally, Azure App Configuration in prod (DEC-021).

Pillar: Stable Core
Phase: KV
Purpose: Pydantic settings; .env locally, Azure App Configuration in prod (DEC-021).
Documented in: docs/deployment/configuration.md
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "maive-backend"
    app_env: str = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Azure Cosmos DB
    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_database: str = "maive"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # LLM Provider: "ollama" (default local/self-hosted) or "azure" (optional paid cloud)
    llm_provider: str = "ollama"

    # Ollama (default local/self-hosted)
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3"
    ollama_embedding_model: str = "nomic-embed-text"

    # Azure AI Foundry / Azure OpenAI (optional paid cloud)
    azure_openai_endpoint: str = ""
    azure_openai_key: str = ""
    azure_openai_chat_deployment: str = ""
    azure_openai_embedding_deployment: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
