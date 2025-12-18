"""
NLP Service Configuration
Loads environment variables and provides settings for the service.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # LLM Provider Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "ollama"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Database Configuration (for schema fetching only)
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "davinci")
    db_user: str = os.getenv("DB_USER", "davinci")
    db_password: str = os.getenv("DB_PASSWORD", "")
    
    # Service Configuration
    nlp_service_host: str = os.getenv("NLP_SERVICE_HOST", "localhost")
    nlp_service_port: int = int(os.getenv("NLP_SERVICE_PORT", "8001"))
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
print(f"DEBUG: Loaded LLM Provider: {settings.llm_provider}")
print(f"DEBUG: Loaded Ollama Model: {settings.ollama_model}")
