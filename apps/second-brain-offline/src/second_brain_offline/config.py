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
    AWS_ACCESS_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("AWS_ACCESS_KEY"),
        description="AWS access key for authentication with AWS services."
    )

    AWS_SECRET_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("AWS_SECRET_KEY"),
        description="AWS secret key for secure authentication with AWS services."
    )

    AWS_CROSS_ACCOUNT_ROLE_ARN: Optional[str] = Field(
        default_factory=lambda: os.getenv("AWS_CROSS_ACCOUNT_ROLE_ARN"),
        description="ARN for cross-account access role in AWS environments."
    )

    AWS_DEFAULT_REGION: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "eu-central-1"),
        description="AWS region where cloud services are deployed."
    )

    AWS_S3_NOSIGN_REQUEST: bool = Field(
        default_factory=lambda: os.getenv("AWS_S3_NOSIGN_REQUEST", False),
        description="Flag to enable unauthenticated S3 bucket access. If True, bypasses AWS authentication."
    )

    AWS_S3_BUCKET_NAME: str = Field(
        default_factory=lambda: os.getenv("AWS_S3_BUCKET_NAME", "decodingml-public-data"),
        description="Name of the S3 bucket containing application data."
    )

    AWS_S3_PREFIX: str = Field(
        default_factory=lambda: os.getenv("AWS_S3_PREFIX", "second_brain_course/notion"),
        description="Prefix path within the S3 bucket for organizing data."
    )

    # --- CometML Configuration ---
    COMET_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("COMET_API_KEY"),
        description="API key for CometML experiment tracking and monitoring."
    )

    COMET_PROJECT_NAME: str = Field(
        default_factory=lambda: os.getenv("COMET_PROJECT_NAME", "twin"),
        description="Project name for organizing experiments in CometML."
    )

    COMET_PROJECT: str = Field(
        default_factory=lambda: os.getenv("COMET_PROJECT", "second_brain_course"),
        description="Project identifier for CometML during training."
    )

    # --- Enable Flags ---
    ENABLE_OFFLINE_MODE: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_OFFLINE_MODE", True),
        description="Flag to enable offline mode (disables online ingestion)."
    )

    # --- GROQ Configuration ---
    GROQ_API_KEY: Optional[str] = Field(
        default_factory=lambda: os.getenv("GROQ_API_KEY"),
        description="API key for accessing GROQ AI services."
    )

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: Optional[str] = Field(
        default_factory=lambda: os.getenv("HUGGINGFACE_ACCESS_TOKEN"),
        description="Access token for Hugging Face model hub and APIs."
    )

    # --- MongoDB Atlas Configuration ---
    MONGODB_DATABASE_NAME: str = Field(
        default_factory=lambda: os.getenv("MONGODB_DATABASE_NAME", "second_brain"),
        description="Name of the MongoDB database for the application."
    )

    MONGODB_OFFLINE_URI: str = Field(
        default_factory=lambda: os.getenv(
            "MONGODB_OFFLINE_URI", 
            "mongodb://decodingml:decodingml@localhost:27017/?directConnection=true"
        ),
        description="Connection URI for the local MongoDB instance."
    )

    MONGODB_ONLINE_URI: Optional[str] = Field(
        default_factory=lambda: os.getenv("MONGODB_ONLINE_URI"),
        description="Connection URI for the cloud MongoDB Atlas instance."
    )

    # --- Notion API Configuration ---
    NOTION_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("NOTION_SECRET_KEY"),
        description="Secret key for authenticating with Notion API."
    )

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="API key for accessing OpenAI services and models."
    )

    OPENAI_MODEL_ID: str = Field(
        default_factory=lambda: os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"),
        description="Identifier for the specific OpenAI model to use."
    )

    # --- RAG Configuration ---
    TEXT_EMBEDDING_MODEL_ID: str = Field(
        default_factory=lambda: os.getenv("TEXT_EMBEDDING_MODEL_ID", "text-embedding-3-small"),
        description="Model identifier for text embedding generation."
    )

    RAG_MODEL_DEVICE: str = Field(
        default_factory=lambda: os.getenv("RAG_MODEL_DEVICE", "cpu"),
        description="Device to run RAG models on (cpu/cuda)."
    )

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

    @field_validator("OPENAI_API_KEY")
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
