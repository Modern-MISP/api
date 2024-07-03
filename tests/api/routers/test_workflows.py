import json
from collections.abc import Sequence
from typing import List

import pytest
from sqlalchemy.future import select

from mmisp.db.models.workflow import Workflow
from mmisp.workflows.legacy import GraphFactory

from ...generators.model_generators.workflow_generator import generate_workflows, genrerate_workflow_with_id


@pytest.fixture
def workflows(db):
    workflows: List[Workflow] = generate_workflows()
    workflows.append(genrerate_workflow_with_id(50))

    for workflow in workflows:
        db.add(workflow)
    db.commit()
    db.refresh(workflow)

    yield workflows

    for workflow in workflows:
        db.delete(workflow)
        db.commit()


def test_workflows_index(db, site_admin_user_token, client, workflows) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/workflows/index", headers=headers)

    result = db.execute(select(Workflow))
    workflows: Sequence[Workflow] = result.scalars().all()

    json_dict = json.loads(response.content.decode())

    for count in range(0, len(workflows)):
        db_workflow = workflows[count]
        response_workflow = json_dict[count]["Workflow"]
        assert db_workflow.id == response_workflow["id"]
        assert db_workflow.uuid == response_workflow["uuid"]


def test_workflow_edit_edit_existing(db, site_admin_user_token, client, workflows) -> None:
    id: int = 50
    headers = {
        "authorization": site_admin_user_token,
    }

    new_workflow = genrerate_workflow_with_id(1)
    data = GraphFactory.graph2jsondict(new_workflow.data)

    payload = {
        "workflow_name": "new workflow name",
        "workflow_description": "new workflow description",
        "workflow_graph": data,
    }
    response = client.post(f"/workflows/edit/{id}", headers=headers, json=payload)

    workflow: Workflow = db.get(Workflow, id)
    db.commit()
    db.refresh(workflow)

    assert response.status_code == 200
    workflow_dict = json.loads(response.content.decode())["Workflow"]
    assert workflow_dict["name"] == payload["workflow_name"]
    assert workflow_dict["description"] == payload["workflow_description"]
    assert workflow_dict["data"] == payload["workflow_graph"]
    assert workflow.name == payload["workflow_name"]
    assert workflow.description == payload["workflow_description"]
    assert workflow.data.nodes == new_workflow.data.nodes
    assert workflow.data.root == new_workflow.data.root
    assert list(workflow.data.frames) == list(new_workflow.data.frames)


def test_workflow_view(client, site_admin_user_token, workflows) -> None:
    id: int = 50
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/view/{id}", headers=headers)

    assert response.status_code == 200
    workflow_dict = json.loads(response.content.decode())["Workflow"]
    assert workflow_dict["id"] == id
    assert workflow_dict["name"] == "Workflow for testing"
    assert workflow_dict["data"]["1"]["class"] == "block-type-trigger"
    assert 1


def test_workflow_view_invalid_id(db, client, site_admin_user_token) -> None:
    id: int = 200
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/view/{id}", headers=headers)

    db_result = db.execute(select(Workflow).where(Workflow.id == id))
    workflow: Workflow = db_result.scalars().first()

    assert response.status_code == 404
    assert workflow is None
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["detail"]["name"] == "Invalid Workflow."
    assert detail_dict["detail"]["message"] == "Invalid Workflow."
    assert detail_dict["detail"]["url"] == f"/workflows/view/{id}"


def test_workflow_delete_success(client, site_admin_user_token, db) -> None:
    id: int = 150
    workflow = genrerate_workflow_with_id(id)
    db.add(workflow)
    db.commit()

    db_result = db.execute(select(Workflow).where(Workflow.id == id))
    workflow: Workflow = db_result.scalars().first()

    assert isinstance(workflow, Workflow)
    assert workflow.id == id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/workflows/delete/{id}", headers=headers)

    db.commit()

    db_result2 = db.execute(select(Workflow).where(Workflow.id == id))
    workflow2: Workflow = db_result2.scalars().first()

    assert response.status_code == 200
    assert workflow2 is None
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["saved"]
    assert detail_dict["success"]
    assert detail_dict["name"] == "Workflow deleted."
    assert detail_dict["message"] == "Workflow deleted."
    assert detail_dict["url"] == f"/workflows/delete/{id}"
    assert (
        detail_dict["id"] == f"{id}"
    )  # WARUM IST DAS JETZT EIN STRING?? in lib.api_schemas.workflows.DeleteWorkflowResponse ist es ein int :(


def test_workflow_delete_invalid_id(client, site_admin_user_token, db) -> None:
    id: int = 200
    db_result = db.execute(select(Workflow).where(Workflow.id == id))
    workflow: Workflow = db_result.scalars().first()

    assert workflow is None

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/workflows/delete/{id}", headers=headers)

    db.commit()

    db_result2 = db.execute(select(Workflow).where(Workflow.id == id))
    workflow2: Workflow = db_result2.scalars().first()

    assert response.status_code == 404
    assert workflow2 is None
    assert str(id) in response.text
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["detail"]["name"] == "Invalid Workflow."
    assert detail_dict["detail"]["message"] == "Invalid Workflow."
    assert detail_dict["detail"]["url"] == f"/workflows/delete/{id}"


def test_db(db):
    workflow = genrerate_workflow_with_id(3)
    db.add(workflow)
    db.commit()
    assert 1


def test_api(site_admin_user_token, client):
    assert 1
