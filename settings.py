# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API keys
    openai_api_key: str
    xai_api_key: str

    model_config = SettingsConfigDict(
        extra="allow", env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
