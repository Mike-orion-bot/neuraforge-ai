"""
CONFIGURACIÓN GLOBAL NEURAFORGE AI
"""
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Telegram Tokens
    MULTIBOT_TELEGRAM_TOKEN: Optional[str] = os.getenv("MULTIBOT_TELEGRAM_TOKEN")
    AFFILIATE_TELEGRAM_TOKEN: Optional[str] = os.getenv("AFFILIATE_TELEGRAM_TOKEN")
    
    # Hotmart API
    HOTMART_CLIENT_ID: Optional[str] = os.getenv("HOTMART_CLIENT_ID")
    HOTMART_CLIENT_SECRET: Optional[str] = os.getenv("HOTMART_CLIENT_SECRET")
    HOTMART_WEBHOOK_SECRET: Optional[str] = os.getenv("HOTMART_WEBHOOK_SECRET")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///neuraforge.db")
    
    # App
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

def validate_settings():
    """Valida configuración mínima"""
    errors = []
    
    if not settings.MULTIBOT_TELEGRAM_TOKEN:
        errors.append("MULTIBOT_TELEGRAM_TOKEN no configurado")
    
    if not settings.AFFILIATE_TELEGRAM_TOKEN:
        errors.append("AFFILIATE_TELEGRAM_TOKEN no configurado")
    
    if not settings.HOTMART_CLIENT_ID:
        errors.append("HOTMART_CLIENT_ID no configurado")
    
    if errors:
        raise ValueError("Errores de configuración:\n" + "\n".join(errors))
