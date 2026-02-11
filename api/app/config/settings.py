
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(
        default="mysql://app_user:app_password@mysql:3306/ecommerce",
        env="DATABASE_URL"
    )

    ELASTICSEARCH_URL: str = Field(
        default="http://elasticsearch:9200",
        env="ELASTICSEARCH_URL"
    )

    DEBUG: bool = Field(default=False, env="DEBUG")
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    SECRET_KEY: str = Field(
        default="b64f8565b393f9101575ec971f0940345840a34d55304530ef7b568987d1f7f5",
           env="SECRET_KEY"
    )
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    INGESTION_WORKERS: int = Field(
        default=8,
        env="INGESTION_WORKERS"
    )

    @computed_field(return_type=Path)
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.parent

    PRODUCT_API_URL: str = Field(
        default="https://dummyjson.com/products",
        env="PRODUCT_API_URL"
    )


settings = Settings()
