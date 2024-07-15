from mmisp.db.models.log import Log
from mmisp.api_schemas.logs import LogsRequest
from mmisp.db.database import Session
import pytest

def test_logs_index(db, site_admin_user_token, client, insert_test_logs) -> None:
    json = LogsRequest(
        model="Workflow",
        model_id=12345678
    ).dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/admin/logs/index", headers=headers, json=json)

    assert response.status_code = 200
    assert "12345678" in response.test

@pytest.fixture()
def insert_test_logs(db: Session):
    log = Log(
        model="Workflow",
        model_id=12345678,
        action="action",
        user_id=1,
        email="admin@admin.test",
        org="awhlud",
        change="Blablabla",
        ip="127.000.000.1"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    yield log

    db.delete(log)
    db.commit()
    db.refresh(log)
