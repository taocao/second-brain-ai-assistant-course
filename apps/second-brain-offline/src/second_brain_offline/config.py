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
    AWS_ACCESS_KEY: str | None = Field(
        default=None, description="AWS access key for authentication."
    )
    AWS_SECRET_KEY: str | None = Field(
        default=None, description="AWS secret key for authentication."
    )
    AWS_CROSS_ACCOUNT_ROLE_ARN: str | None = Field(
        default=None, description="ARN for AWS cross-account access role."
    )
    AWS_DEFAULT_REGION: str = Field(
        default="eu-central-1", description="AWS region for cloud services."
    )
    AWS_S3_BUCKET_NAME: str = Field(
        default="decodingml-public-data",
        description="Name of the S3 bucket for storing application data.",
    )
    AWS_S3_NOSIGN_REQUEST: bool = Field(
        default=False,
        description="Flag to enable unauthenticated S3 bucket access. If True, bypasses AWS authentication.",
    )

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="second_brain_course",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Flags ---
    IS_OFFLINE_MODE: bool = Field(
        default=True,
        description="Flag to enable offline mode (disables online/cloud services).",
    )

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: str | None = Field(
        default=None, description="Access token for Hugging Face API authentication."
    )

    # --- MongoDB Atlas Configuration ---
    MONGODB_DATABASE_NAME: str = Field(
        default="second_brain_course",
        description="Name of the MongoDB database.",
    )
    MONGODB_OFFLINE_URI: str = Field(
        default="mongodb://decodingml:decodingml@localhost:27017/?directConnection=true",
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    MONGODB_ONLINE_URI: str | None = Field(
        default=None,
        description="Connection URI for the Cloud MongoDB Atlas instance.",
    )

    # --- Notion API Configuration ---
    NOTION_SECRET_KEY: str | None = Field(
        default=None, description="Secret key for Notion API authentication."
    )

    # --- Groq Configuration ---
    GROQ_API_KEY: str | None = Field(
        default=None, description="API key for Groq service authentication."
    )

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication.",
    )
    OPENAI_MODEL_ID: str = Field(
        default="gpt-4o-mini", description="Identifier for the OpenAI model to be used."
    )

    # --- RAG Configuration ---
    TEXT_EMBEDDING_MODEL_ID: str = Field(
        default="text-embedding-3-small",
        description="Model identifier for text embedding generation.",
    )
    RAG_MODEL_DEVICE: str = Field(
        default="cpu",
        description="Device to run RAG models on (cpu/cuda).",
    )

    @property
    def MONGODB_URI(self) -> str:
        """
        Returns the appropriate MongoDB URI based on ENABLE_OFFLINE_MODE.
        """
        if self.IS_OFFLINE_MODE is True:
            return self.MONGODB_OFFLINE_URI

        assert self.MONGODB_ONLINE_URI is not None, (
            "MONGODB_ONLINE_URI is not set, while ENABLE_OFFLINE_MODE is False."
        )

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
