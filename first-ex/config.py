import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent
try:
    load_dotenv(dotenv_path=ENV_PATH)
except Exception:
    pass

api_key = os.getenv("OPENAI_KEY")

class Settings(BaseSettings):
    app_name: str = "My API"
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "asdfasdfasdfasdf-asdfasdfaf"
    debug: bool = False
    api_key: str = "api_key"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="allow",
    )

@lru_cache()
def get_settings():
    return Settings()