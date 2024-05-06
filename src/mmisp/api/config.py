from os import getenv

from dotenv import load_dotenv
from pydantic.dataclasses import dataclass


@dataclass
class APIConfig:
    HASH_SECRET: str
    WORKER_KEY: str
    OWN_URL: str
    WORKER_URL: str
    DASHBOARD_URL: str
    READONLY_MODE: bool


load_dotenv(getenv("ENV_FILE", ".env"))

config: APIConfig = APIConfig(
    HASH_SECRET=getenv("HASH_SECRET", ""),
    WORKER_KEY=getenv("WORKER_KEY", ""),
    OWN_URL=getenv("OWN_URL", ""),
    WORKER_URL=getenv("WORKER_URL", ""),
    DASHBOARD_URL=getenv("DASHBOARD_URL", ""),
    READONLY_MODE=bool(getenv("READONLY_MODE", False)),
)
