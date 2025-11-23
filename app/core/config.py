from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # ippanel SMS
    ippanel_api_key: str = os.getenv("IPPANEL_API_KEY")
    ippanel_sender_number: Optional[str] = os.getenv("IPPANEL_SENDER_NUMBER")
    
    # App
    debug: bool = os.getenv("DEBUG")
    app_name: str = os.getenv("APP_NAME")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

