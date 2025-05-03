from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MathSolver"  # demo MVP
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./logs.db"
    OPENAI_API_KEY : str = "yourkey"
    
    LLM_MODEL: str = 'gpt-4o-mini'
    
    CREATE_EMBEDDINGS : bool = True

    class Config:
        env_file = ".env"

settings = Settings()