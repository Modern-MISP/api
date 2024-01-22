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


load_dotenv(".env")


config: ConfigType = ConfigType(
    DATABASE_URL=getenv("DATABASE_URL") or "",
    HASH_SECRET=getenv("HASH_SECRET") or "",
    WORKER_KEY=getenv("WORKER_KEY") or "",
    WORKER_URL=getenv("WORKER_URL") or "",
    DASHBOARD_URL=getenv("DASHBOARD_URL"),
)
