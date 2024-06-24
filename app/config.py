from typing import Optional

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    neo4j_uri: Optional[str] = None
    neo4j_database: str = "neo4j"


settings = Settings()
