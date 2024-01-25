from typing import Any

from fastapi.testclient import TestClient

from mmisp.api.main import app

# test init code (database setup, other initializing)
# generate test environment object which includes user_token + other relevant data

environment: Any = ""

client = TestClient(app)
