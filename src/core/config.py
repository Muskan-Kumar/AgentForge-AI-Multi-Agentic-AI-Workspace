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

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
