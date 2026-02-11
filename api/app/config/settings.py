
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql://app_user:app_password@mysql:3306/ecommerce"
    elasticsearch_url: str = "http://elasticsearch:9200"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    secret_key: str = "your-secret-key-here-change-in-production"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    
    

settings = Settings()
