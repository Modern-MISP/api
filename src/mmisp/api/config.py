"""This module handels the configuration of the API.

Database related settings are part of mmisp.db of the lib repository.
"""

import logging
from enum import StrEnum
from os import getenv

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Runner(StrEnum):
    GUNICORN = "gunicorn"
    GRANIAN = "granian"


class APIConfig(BaseSettings):
    HASH_SECRET: str
    WORKER_KEY: str
    WORKER_URL: str
    OWN_URL: str = ""
    DASHBOARD_URL: str = ""
    READONLY_MODE: bool = False
    ENABLE_PROFILE: bool = False
    DEBUG: bool = False
    ENABLE_TEST_ENDPOINTS: bool = False

    RUNNER: Runner = Runner.GUNICORN
    PORT: int = 4000
    BIND_HOST: str = "0.0.0.0"
    WORKER_COUNT: int = 4


load_dotenv(getenv("ENV_FILE", ".env"))

config: APIConfig = APIConfig()

logger = logging.getLogger("mmisp")
logger.setLevel(logging.INFO)
if config.DEBUG:
    logger.setLevel(logging.DEBUG)
