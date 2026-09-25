from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str
    TAVILY_API_KEY: str

    POSTGRES_URL: str

    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str

    GROQ_MODEL:str
    EMBEDDING_MODEL: str

    HF_TOKEN:str
    IMAGE_MODEL:str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
