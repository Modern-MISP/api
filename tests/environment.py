from fastapi.testclient import TestClient

from mmisp.api.main import app
from mmisp.db.database import Base
from tests.database import engine

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def auth_header(token: str) -> dict:
    return {"authorization": f"Bearer {token}"}
