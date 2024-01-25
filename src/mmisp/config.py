from os import getenv

from dotenv import load_dotenv


class ConfigType:
    def __init__(
        self,
        DATABASE_URL: str,
        HASH_SECRET: str,
        WORKER_KEY: str,
        WORKER_URL: str,
        DASHBOARD_URL: str | None = None,
    ):
        self.DATABASE_URL = DATABASE_URL
        self.HASH_SECRET = HASH_SECRET
        self.WORKER_KEY = WORKER_KEY
        self.WORKER_URL = WORKER_URL
        self.DASHBOARD_URL = DASHBOARD_URL


load_dotenv(getenv("ENV_FILE", ".env"))


config: ConfigType = ConfigType(
    DATABASE_URL=getenv("DATABASE_URL", ""),
    HASH_SECRET=getenv("HASH_SECRET", ""),
    WORKER_KEY=getenv("WORKER_KEY", ""),
    WORKER_URL=getenv("WORKER_URL", ""),
    DASHBOARD_URL=getenv("DASHBOARD_URL"),
)
