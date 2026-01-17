from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dishwasher Workflow System"
    API_V1_STR: str = "/api/v1"

    # Database
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Uploads
    UPLOAD_DIR: str = "uploads"

    class Config:
        case_sensitive = True

settings = Settings()
