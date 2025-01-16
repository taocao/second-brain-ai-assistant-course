"""
Module:
config.py

This module defines a `Settings` class for managing application configurations using Pydantic v2.
It supports loading configuration values from a `.env` file and includes validation for required fields.

Attributes:
    AWS_ACCESS_KEY (Optional[str]): AWS access key for authentication.
    AWS_CROSS_ACCOUNT_ROLE_ARN (Optional[str]): ARN for AWS cross-account access role.
    AWS_REGION (str): AWS region for cloud services.
    AWS_S3_BUCKET_NAME (str): Name of the S3 bucket for storing application data.
    AWS_SECRET_KEY (Optional[str]): AWS secret key for authentication.
    COMET_API_KEY (Optional[str]): API key for CometML integration.
    COMET_PROJECT_NAME (str): CometML project name for tracking experiments.
    DEFAULT_GENRE (str): Default genre for querying.
    DOCKER_NETWORK_NAME (str): Docker network for inter-container communication.
    ENABLE_MONGODB_ATLAS_INGESTION (bool): Flag to enable ingestion from MongoDB Atlas.
    ENABLE_OFFLINE_MODE (bool): Flag to enable offline mode (disables online ingestion).
    ENABLE_STRUCTURED_LOGGING (bool): Enable or disable structured logging.
    GROQ_API_KEY (Optional[str]): API key for accessing GROQ services.
    HUGGINGFACE_ACCESS_TOKEN (Optional[str]): Token for Hugging Face API.
    IS_RUNNING_IN_DOCKER (bool): Flag to indicate if the application is running inside a Docker container.
    LOCAL_JSON_FILE_PATH (str): Path to the local JSON file for offline processing.
    LOG_DIR (str): Directory path for log files.
    MAX_FETCH_LIMIT (int): Maximum number of documents to fetch from the database.
    MAX_LENGTH (int): Maximum length for summarization.
    MODEL_NAME (str): Default model for summarization.
    MONGODB_OFFLINE_COLLECTION (str): Name of the collection in the offline database.
    MONGODB_OFFLINE_DATABASE (str): Name of the offline database.
    MONGODB_OFFLINE_URI (str): Connection URI for local MongoDB instance.
    MONGODB_ONLINE_COLLECTION (str): Name of the collection in the online database.
    MONGODB_ONLINE_DATABASE (str): Name of the online database.
    MONGODB_ONLINE_URI (str): MongoDB Atlas URI.
    NOTION_SECRET_KEY (str): Secret key for accessing Notion API.
    OPENAI_API_KEY (str): API key for accessing OpenAI services.
    OPENAI_MODEL_IDENTIFIER (str): Model identifier for OpenAI.

Features:
- Dynamically toggles between MongoDB Atlas (online) and local JSON (offline) data ingestion.
- Provides defaults and validates required fields.
- Calculates derived properties such as OpenAI token limits.
- Supports configurations for external APIs, database connections, and environment settings.

Dependencies:
- `pydantic_settings` for structured settings management.
- `pydantic` for field validation.

Usage:
    The `Settings` class is instantiated automatically and validates required fields. The configurations are accessed through its attributes.

Methods:
    LOG_FILE: Returns the log file path.
    MONGODB_URI: Determines the active MongoDB URI based on mode.
"""

import logging
import os
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# TODO: Replace all current logger configurations with loguru.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """

    # --- AWS Configuration ---
    AWS_ACCESS_KEY: Optional[str] = None  # AWS access key for authentication.
    AWS_CROSS_ACCOUNT_ROLE_ARN: Optional[str] = (
        None  # ARN for AWS cross-account access role.
    )
    AWS_DEFAULT_REGION: str = "eu-central-1"  # AWS region for cloud services.
    AWS_S3_BUCKET_NAME: str = (
        "decodingml-public-data"  # Name of the S3 bucket for storing application data.
    )
    AWS_SECRET_KEY: Optional[str] = None  # AWS secret key for authentication.

    # --- CometML Configuration ---
    COMET_API_KEY: Optional[str] = None  # API key for CometML integration.
    COMET_PROJECT_NAME: str = "twin"  # CometML project name for tracking experiments.

    # --- Default Genre ---
    DEFAULT_GENRE: str = Field("Western", description="Default genre for querying.")

    # --- Docker and Network Configuration ---
    DOCKER_NETWORK_NAME: str = Field(
        "zenml-network", description="Docker network for the application."
    )

    # --- Enable Flags ---
    ENABLE_MONGODB_ATLAS_INGESTION: bool = Field(
        False, description="Flag to enable ingestion from MongoDB Atlas."
    )
    ENABLE_OFFLINE_MODE: bool = Field(
        True, description="Flag to enable offline mode (disables online ingestion)."
    )
    ENABLE_STRUCTURED_LOGGING: bool = Field(
        True,
        description="Enable or disable structured logging. Default is True (enabled).",
    )

    # --- GROQ Configuration ---
    GROQ_API_KEY: Optional[str] = None  # API key for accessing GROQ services.

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: Optional[str] = None  # Token for Hugging Face API.

    # --- Local Data File Path ---
    LOCAL_JSON_FILE_PATH: str = Field(
        "./data/documents_dump.json",
        description="Path to the local JSON file for offline processing.",
    )

    # --- Logging Configuration ---
    LOG_DIR: str = "./logs"  # Directory path for log files.

    # --- MongoDB Offline Configuration ---
    MONGODB_OFFLINE_COLLECTION: str = (
        "offline_documents"  # Name of the collection in the offline database.
    )
    MONGODB_OFFLINE_DATABASE: str = "rag_pipeline"  # Name of the offline database.
    MONGODB_OFFLINE_URI: str = Field(
        default_factory=lambda: os.getenv(
            "MONGODB_OFFLINE_URI", "mongodb://mongodb-atlas-local:27017"
        ),
        description="Connection URI for local MongoDB instance.",
    )

    # --- MongoDB Online Configuration ---
    MONGODB_ONLINE_COLLECTION: str = (
        "movies"  # Name of the collection in the online database.
    )
    MONGODB_ONLINE_DATABASE: str = "sample_mflix"  # Name of the online database.
    MONGODB_ONLINE_URI: str  # MongoDB Atlas URI.

    # --- Notion API Configuration ---
    NOTION_SECRET_KEY: str  # Secret key for accessing Notion API.

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str  # API key for accessing OpenAI services.
    OPENAI_MODEL_IDENTIFIER: str = "gpt-4o-mini"  # Model identifier for OpenAI.

    # --- Summarization Configuration ---
    MAX_FETCH_LIMIT: int = Field(
        200, ge=1, description="Maximum number of documents to fetch."
    )
    MAX_LENGTH: int = Field(100, ge=10, description="Maximum length for summarization.")
    MODEL_NAME: str = "t5-small"  # Default model for summarization.

    # --- Docker Runtime ---
    IS_RUNNING_IN_DOCKER: bool = Field(
        default_factory=lambda: os.getenv("IS_RUNNING_IN_DOCKER", "false").lower()
        in ["true", "1"],
        description="Flag to indicate if the application is running inside a Docker container.",
    )

    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    def __init__(self, **kwargs):
        """
        Dynamically adjusts configurations based on flags like IS_RUNNING_IN_DOCKER or ENABLE_OFFLINE_MODE.
        """
        super().__init__(**kwargs)

        # Adjust MongoDB URI based on runtime conditions, but respect .env
        if os.getenv("IS_RUNNING_IN_DOCKER", "false").lower() == "true":
            self.MONGODB_OFFLINE_URI = os.getenv(
                "MONGODB_OFFLINE_URI", "mongodb://mongodb-atlas-local:27017"
            )

        if not self.ENABLE_OFFLINE_MODE:
            self.MONGODB_OFFLINE_URI = self.MONGODB_ONLINE_URI

        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

    @property
    def LOG_FILE(self) -> str:
        """
        Returns the full path to the log file.
        """
        return str(Path(self.LOG_DIR) / "mongodb_atlas_pipeline.log")

    @property
    def MONGODB_URI(self) -> str:
        """
        Returns the appropriate MongoDB URI based on ENABLE_OFFLINE_MODE.
        """
        return (
            self.MONGODB_OFFLINE_URI
            if self.ENABLE_OFFLINE_MODE
            else self.MONGODB_ONLINE_URI
        )

    @property
    def DATABASE_NAME(self) -> str:
        """
        Returns the appropriate database name based on ENABLE_OFFLINE_MODE.
        """
        return (
            self.MONGODB_OFFLINE_DATABASE
            if self.ENABLE_OFFLINE_MODE
            else self.MONGODB_ONLINE_DATABASE
        )

    @property
    def COLLECTION_NAME(self) -> str:
        """
        Returns the appropriate collection name based on ENABLE_OFFLINE_MODE.
        """
        return (
            self.MONGODB_OFFLINE_COLLECTION
            if self.ENABLE_OFFLINE_MODE
            else self.MONGODB_ONLINE_COLLECTION
        )

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
        return int(model_token_limits.get(self.OPENAI_MODEL_IDENTIFIER, 128000) * 0.90)

    @field_validator(
        "OPENAI_API_KEY",
        "MONGODB_ONLINE_URI",
        "MONGODB_ONLINE_DATABASE",
        "MONGODB_ONLINE_COLLECTION",
        "NOTION_SECRET_KEY",
        mode="before",
    )
    def check_not_empty(cls, value: str, field) -> str:
        if not value or value.strip() == "":
            logger.error(f"{field.name} cannot be empty.")
            raise ValueError(f"{field.name} cannot be empty.")
        return value


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)
