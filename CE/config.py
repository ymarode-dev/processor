from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CORE_DATABASE_URL: str = "sqlite+aiosqlite:////CE/db/data/sql/core.db"
    PC_DATABASE_URL: str = "sqlite+aiosqlite:////CE/db/data/sql/pc.db"
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    # REDIS_PASSWORD: str
    MQTT_HOST: str = "127.0.0.1"
    MQTT_PORT: int = 8886
    MQTT_USERNAME: str = "CEDPython"
    MQTT_PASSWORD: str = "@$0uL|?yT#0n"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()