"""
NLP Service Configuration
Loads environment variables and provides settings for the service.
"""
import os
import sys
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Django Integration
    # The NLP service now fetches schema from the Django URL, ensuring security boundary
    django_api_url: str = os.getenv("DJANGO_API_URL", "http://127.0.0.1:8000")
    
    # Service Configuration
    nlp_service_host: str = os.getenv("NLP_SERVICE_HOST", "localhost")
    nlp_service_port: int = int(os.getenv("NLP_SERVICE_PORT", "8003"))
    
    # Groq API Configuration (REQUIRED - Get key from https://console.groq.com/keys)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model_name: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Rate Limiting - Higher limits for better UX (adjust via env vars if hitting Groq limits)
    # Groq paid tier: 100 req/min, 100k tokens/min
    max_requests_per_minute: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    max_tokens_per_minute: int = int(os.getenv("MAX_TOKENS_PER_MINUTE", "50000"))
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "512"))

    class Config:
        env_file = ".env"
        extra = "allow"



settings = Settings()

# Validate required settings
if not settings.groq_api_key:
    print("=" * 60)
    print("ERROR: GROQ_API_KEY is not set!")
    print("=" * 60)
    print("Please set your Groq API key in the .env file:")
    print("  1. Copy .env.example to .env")
    print("  2. Get your FREE API key from: https://console.groq.com/keys")
    print("  3. Set GROQ_API_KEY=your_key_here in .env")
    print("=" * 60)
    sys.exit(1)

