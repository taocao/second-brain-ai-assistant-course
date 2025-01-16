from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Required settings when exporting your Notion data. ---

    NOTION_SECRET_KEY: str | None = None

    # --- Required settings even when working locally. ---
    AWS_DEFAULT_REGION: str = "eu-central-1"
    AWS_S3_BUCKET_NAME: str = "decodingml-public-data"

    # OpenAI API
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None

    # Groq API
    GROQ_API_KEY: str | None = None

    # Huggingface API
    HUGGINGFACE_ACCESS_TOKEN: str | None = None

    # Comet ML (during training)
    COMET_API_KEY: str | None = None
    COMET_PROJECT: str = "twin"

    # --- Required settings when deploying the code. ---
    # --- Otherwise, default values values work fine. ---

    # MongoDB database
    DATABASE_HOST: str = "mongodb://llm_engineering:llm_engineering@127.0.0.1:27017"
    DATABASE_NAME: str = "twin"

    # AWS Authentication
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    @property
    def OPENAI_MAX_TOKEN_WINDOW(self) -> int:
        official_max_token_window = {
            "gpt-3.5-turbo": 16385,
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
        }.get(self.OPENAI_MODEL_ID, 128000)

        max_token_window = int(official_max_token_window * 0.90)

        return max_token_window


settings = Settings()
