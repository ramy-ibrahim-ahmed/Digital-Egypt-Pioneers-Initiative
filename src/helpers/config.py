from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    COLLEGE_SCRAPING_SITE: str
    TRANSCRIPT_DOWNLOAD_LINK: str
    EXTRACT_STUDENT_INFORMATION_PROMPT: str
    MONGODB_URL: str
    MONGODB_DATABASE: str
    EMBEDDING_MODEL: Optional[str] = ""

    class Config:
        env_file = ".env"


def get_settings():
    settings = Settings()
    return settings
