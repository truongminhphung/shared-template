from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file explicitly (useful for local development outside Docker)
load_dotenv()


class Config(BaseSettings):
    app_name: str = "ScalableFastAPIProject"
    debug: bool = False

    # Database Configuration
    db_user: str
    db_password: str
    db_name: str
    # Default to localhost/5432 for local testing,
    # but Docker will override this with 'db' via the DB_HOST env var.
    db_host: str = "localhost"
    db_port: int = 5432

    @property
    def db_url(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


config = Config()
