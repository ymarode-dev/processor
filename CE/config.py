from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CORE_DATABASE_URL: str
    PC_DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    # REDIS_PASSWORD: str
    MQTT_HOST: str
    MQTT_PORT: int
    # MQTT_USERNAME: str
    # MQTT_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()