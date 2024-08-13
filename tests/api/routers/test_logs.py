import json

import pytest
import sqlalchemy as sa

from mmisp.api_schemas.logs import LogsRequest
from mmisp.db.database import Session
from mmisp.db.models.log import Log


def test_logs_index(site_admin_user_token, client, log_entry, db) -> None:
    json_req = LogsRequest(model="Workflow", model_id=12345678).dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/logs/index", headers=headers, json=json_req)

    assert response.status_code == 200
    json_dict = json.loads(response.content.decode())

    assert len(json_dict) == 1
    assert json_dict[0]["Log"]["model_id"] == "12345678"
    assert json_dict[0]["Log"]["model"] == "Workflow"


def test_logs_noresult(site_admin_user_token, client, log_entry, db) -> None:
    json_req = LogsRequest(model="User", model_id=12345678).dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/logs/index", headers=headers, json=json_req)

    assert response.status_code == 200
    json_dict = json.loads(response.content.decode())

    assert len(json_dict) == 0


@pytest.fixture()
def log_entry(db: Session):
    # Ensure clean slate, other tests also log and there's
    # no centralized cleaning up for that so far.
    db.execute(sa.delete(Log))
    db.commit()
    log = Log(
        model="Workflow",
        model_id=12345678,
        action="action",
        user_id=1,
        email="admin@admin.test",
        org="awhlud",
        change="data(a -> b)",
        ip="127.000.000.1",
    )
    db.add(log)
    db.commit()

    yield log

    db.delete(log)
    db.commit()
