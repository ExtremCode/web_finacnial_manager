from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    host: str = "localhost"
    db_name: str = "financial"
    user: str = "postgres"
    password: str = "rootroot"

    @property
    def url(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}/{self.db_name}"
