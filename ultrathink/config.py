"""Configuration management for Ultrathink"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenRouter
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")

    # TickTick OAuth
    ticktick_client_id: str = Field(..., alias="TICKTICK_CLIENT_ID")
    ticktick_client_secret: str = Field(..., alias="TICKTICK_CLIENT_SECRET")
    ticktick_redirect_uri: str = Field(
        default="http://localhost:8000/callback",
        alias="TICKTICK_REDIRECT_URI"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./ultrathink.db",
        alias="DATABASE_URL"
    )

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # Frontend URL for OAuth redirects after authentication
    frontend_url: str = Field(
        default="http://localhost:5173",
        alias="FRONTEND_URL"
    )

    # AI Model
    ai_model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        alias="AI_MODEL"
    )
    ai_temperature: float = Field(default=0.7, alias="AI_TEMPERATURE")

    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")

    # Gmail OAuth (optional)
    gmail_client_id: str = Field(default="", alias="GMAIL_CLIENT_ID")
    gmail_client_secret: str = Field(default="", alias="GMAIL_CLIENT_SECRET")
    gmail_redirect_uri: str = Field(
        default="http://localhost:8000/email/gmail/callback",
        alias="GMAIL_REDIRECT_URI"
    )

    # Outlook OAuth (optional)
    outlook_client_id: str = Field(default="", alias="OUTLOOK_CLIENT_ID")
    outlook_client_secret: str = Field(default="", alias="OUTLOOK_CLIENT_SECRET")
    outlook_tenant_id: str = Field(default="common", alias="OUTLOOK_TENANT_ID")
    outlook_redirect_uri: str = Field(
        default="http://localhost:8000/email/outlook/callback",
        alias="OUTLOOK_REDIRECT_URI"
    )

    # TickTick API endpoints
    ticktick_oauth_url: str = "https://ticktick.com/oauth/authorize"
    ticktick_token_url: str = "https://ticktick.com/oauth/token"
    ticktick_api_base: str = "https://api.ticktick.com/open/v1"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
