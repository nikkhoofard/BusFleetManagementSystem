from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # ippanel SMS
    ippanel_api_key: str
    ippanel_sender_number: Optional[str] = None
    
    # App
    debug: bool = True
    app_name: str = "Bus Fleet Management System"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

