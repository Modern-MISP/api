from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


@dataclass
class APIConfig:
    HASH_SECRET: str
    WORKER_KEY: str
    OWN_URL: str
    WORKER_URL: str
    DASHBOARD_URL: str


load_dotenv(getenv("ENV_FILE", ".env"))

config: APIConfig = APIConfig(
    HASH_SECRET=getenv("HASH_SECRET", ""),
    WORKER_KEY=getenv("WORKER_KEY", ""),
    OWN_URL=getenv("OWN_URL", ""),
    WORKER_URL=getenv("WORKER_URL", ""),
    DASHBOARD_URL=getenv("DASHBOARD_URL", ""),
)
