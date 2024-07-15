import pytest

from mmisp.api_schemas.logs import LogsRequest
from mmisp.db.database import Session
from mmisp.db.models.log import Log


@pytest.mark.parametrize("insert_test_logs", [5], indirect=True)  # Adjust the number as needed
def test_logs_index(db, site_admin_user_token, client, insert_test_logs) -> None:
    json = LogsRequest(model="Workflow", model_id=12345678).dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/admin/logs/index", headers=headers, json=json)

    assert response.status_code == 200
    assert "12345678" in response.text


@pytest.fixture()
def insert_test_logs(db: Session, request):
    n = request.param

    logs = []

    for i in range(n):
        log = Log(
            model="Workflow",
            model_id=12345678,
            action="action",
            user_id=1,
            email="admin@admin.test",
            org="awhlud",
            change=f"Blablabla{i}",
            ip="127.000.000.1",
        )
        logs.append(log)
        db.add(log)
        db.commit()
        db.refresh(log)

    yield logs

    for log in logs:
        db.delete(log)
        db.commit()
        db.refresh(log)
