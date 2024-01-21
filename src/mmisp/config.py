from os import getenv

from dotenv import load_dotenv


class ConfigType:
    def __init__(
        self,
        DATABASE_URL: str,
        HASH_SECRET: str,
        DASHBOARD_URL: str | None = None,
    ):
        self.DATABASE_URL = DATABASE_URL
        self.HASH_SECRET = HASH_SECRET
        self.DASHBOARD_URL = DASHBOARD_URL


load_dotenv(".env")


config: ConfigType = ConfigType(
    DATABASE_URL=getenv("DATABASE_URL") or "",
    HASH_SECRET=getenv("HASH_SECRET") or "",
    DASHBOARD_URL=getenv("DASHBOARD_URL"),
)
