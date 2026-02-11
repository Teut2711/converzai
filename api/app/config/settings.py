
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="mysql://app_user:app_password@mysql:3306/ecommerce",
        env="DATABASE_URL"
    )

    elasticsearch_url: str = Field(
        default="http://elasticsearch:9200",
        env="ELASTICSEARCH_URL"
    )

    debug: bool = Field(default=False, env="DEBUG")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    secret_key: str = Field(
        default="b64f8565b393f9101575ec971f0940345840a34d55304530ef7b568987d1f7f5",
           env="SECRET_KEY"
    )
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    PRODUCT_API_URL: str = Field(
        default="https://dummyjson.com/products",
        env="PRODUCT_API_URL"
    )

    @computed_field(return_type=Path)
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.parent


settings = Settings()
