import os
from typing import Optional

from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """

    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # --- AWS Configuration ---
    AWS_ACCESS_KEY: Optional[str] = None  # AWS access key for authentication.
    AWS_SECRET_KEY: Optional[str] = None  # AWS secret key for authentication.
    AWS_CROSS_ACCOUNT_ROLE_ARN: Optional[str] = (
        None  # ARN for AWS cross-account access role.
    )

    AWS_DEFAULT_REGION: str = "eu-central-1"  # AWS region for cloud services.
    AWS_S3_BUCKET_NAME: str = (
        "decodingml-public-data"  # Name of the S3 bucket for storing application data.
    )

    # --- CometML Configuration ---
    COMET_API_KEY: Optional[str] = None  # API key for CometML integration.
    COMET_PROJECT_NAME: str = "twin"  # CometML project name for tracking experiments.

    # --- Enable Flags ---
    ENABLE_OFFLINE_MODE: bool = Field(
        True, description="Flag to enable offline mode (disables online ingestion)."
    )

    # --- GROQ Configuration ---
    GROQ_API_KEY: Optional[str] = None  # API key for accessing GROQ services.

    # Comet ML (during training)
    COMET_API_KEY: str | None = None
    COMET_PROJECT: str = "second_brain_course"

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: Optional[str] = None  # Token for Hugging Face API.

    # --- MongoDB Atlas Configuration ---
    MONGODB_DATABASE_NAME: str = "second_brain"
    MONGODB_OFFLINE_URI: str = Field(
        default_factory=lambda: os.getenv(
            "MONGODB_OFFLINE_URI",
            "mongodb://decodingml:decodingml@localhost:27017/?directConnection=true",
        ),
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    MONGODB_ONLINE_URI: str | None = Field(
        default=None,
        description="Connection URI for the Cloud MongoDB Atlas instance.",
    )

    # --- Notion API Configuration ---
    NOTION_SECRET_KEY: str  # Secret key for accessing Notion API.

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str  # API key for accessing OpenAI services.
    OPENAI_MODEL_ID: str = "gpt-4o-mini"  # Model identifier for OpenAI.

    # --- RAG Configuration ---
    TEXT_EMBEDDING_MODEL_ID: str = "text-embedding-3-small"
    RAG_MODEL_DEVICE: str = "cpu"

    @property
    def MONGODB_URI(self) -> str:
        """
        Returns the appropriate MongoDB URI based on ENABLE_OFFLINE_MODE.
        """

        if self.ENABLE_OFFLINE_MODE is True:
            return self.MONGODB_OFFLINE_URI

        assert (
            self.MONGODB_ONLINE_URI is not None
        ), "MONGODB_ONLINE_URI is not set, while ENABLE_OFFLINE_MODE is False."

        return self.MONGODB_ONLINE_URI

    @property
    def OPENAI_MAX_TOKEN_WINDOW(self) -> int:
        """
        Calculates the maximum token window for the configured OpenAI model. Returns 90% of the token limit for safety margin.
        """

        model_token_limits = {
            "gpt-3.5-turbo": 16385,
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
        }
        return int(model_token_limits.get(self.OPENAI_MODEL_ID, 128000) * 0.90)

    @field_validator(
        "OPENAI_API_KEY",
    )
    @classmethod
    def check_not_empty(cls, value: str, info) -> str:
        if not value or value.strip() == "":
            logger.error(f"{info.field_name} cannot be empty.")
            raise ValueError(f"{info.field_name} cannot be empty.")
        return value


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)
