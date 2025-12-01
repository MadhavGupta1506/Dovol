from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    database_ssl: bool = False
    secret_key: str
    algorithm: str
    access_token_expire_days: int
    
    # Email/SMTP settings for password reset
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    
    class Config:
        env_file = ".env"  # Updated path to .env
        case_sensitive = False

settings = Settings()