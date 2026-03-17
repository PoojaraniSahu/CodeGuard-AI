import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    # Using a tool like ngrok for local webhook testing:
    WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./codeguard.db")

settings = Settings()
