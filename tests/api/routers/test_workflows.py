import json
from collections.abc import Sequence
from typing import List, cast

import pytest
from sqlalchemy.future import select

from mmisp.db.database import Session
from mmisp.db.models.admin_setting import AdminSetting
from mmisp.db.models.workflow import Workflow
from mmisp.workflows.graph import WorkflowGraph
from mmisp.workflows.legacy import GraphFactory
from mmisp.workflows.modules import MODULE_REGISTRY, TRIGGER_REGISTRY, Module, Trigger

from ...generators.model_generators.workflow_generator import (
    generate_workflows,
    genrerate_workflow_with_id,
)


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
        assert str(db_workflow.id) == response_workflow["id"]
        assert db_workflow.uuid == response_workflow["uuid"]


# idk how to give form data into an request. will try later
def test_workflow_edit_edit_existing(db, site_admin_user_token, client) -> None:
    id: int = 50
    headers = {
        "authorization": site_admin_user_token,
        "accept": "application/json",
    }

    new_workflow = genrerate_workflow_with_id(id)
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)
    data = json.dumps(GraphFactory.graph2jsondict(new_workflow.data))

    payload = {
        "data[Workflow][name]": "new workflow name",
        "data[Workflow][description]": "new workflow description",
        "data[Workflow][data]": data,
    }
    response = client.post(f"/workflows/edit/{id}", headers=headers, data=payload)

    assert response.status_code == 200

    workflow: Workflow = db.get(Workflow, id)
    db.commit()
    db.refresh(new_workflow)
    workflow_dict = json.loads(response.content.decode())["Workflow"]
    assert workflow_dict["name"] == payload["data[Workflow][name]"]
    assert workflow_dict["description"] == payload["data[Workflow][description]"]
    assert workflow_dict["data"] == json.loads(data)
    assert workflow.name == payload["data[Workflow][name]"]
    assert workflow.description == payload["data[Workflow][description]"]
    assert workflow.data.nodes == new_workflow.data.nodes
    assert workflow.data.root == new_workflow.data.root
    assert list(workflow.data.frames) == list(new_workflow.data.frames)

    db.delete(new_workflow)
    db.commit()


def test_edit_workflow_invalid(db, site_admin_user_token, client, workflows) -> None:
    headers = {
        "authorization": site_admin_user_token,
        "accept": "application/json",
    }

    new_workflow = workflows[1]
    data = GraphFactory.graph2jsondict(new_workflow.data)
    id: int = new_workflow.id

    data["1"]["outputs"]["output_1"]["connections"] = [{"node": "1", "output": "input_1"}]

    data_enc = json.dumps(data)

    payload = {
        "data[Workflow][name]": "new workflow name",
        "data[Workflow][description]": "new workflow description",
        "data[Workflow][data]": data_enc,
    }
    response = client.post(f"/workflows/edit/{id}", headers=headers, data=payload)

    assert response.status_code == 400


def test_workflow_view(client, site_admin_user_token, workflows) -> None:
    id: int = 50
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/view/{id}", headers=headers)

    assert response.status_code == 200
    workflow_dict = json.loads(response.content.decode())["Workflow"]
    assert workflow_dict["id"] == str(id)
    assert workflow_dict["name"] == "Workflow for testing"
    assert workflow_dict["data"]["1"]["class"] == "block-type-trigger"


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

    workflow = db.get(Workflow, id)

    assert isinstance(workflow, Workflow)
    assert workflow.id == id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/workflows/delete/{id}", headers=headers)

    db.expire(workflow)
    workflow2 = db.get(Workflow, id)

    assert response.status_code == 200
    assert workflow2 is None
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["saved"]
    assert detail_dict["success"]
    assert detail_dict["name"] == "Workflow deleted."
    assert detail_dict["message"] == "Workflow deleted."
    assert detail_dict["url"] == f"/workflows/delete/{id}"
    assert detail_dict["id"] == f"{id}"


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


def test_workflow_editor_create_new_workflow(client, site_admin_user_token, db) -> None:
    trigger_id = "attribute-after-save"
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/workflows/editor/{trigger_id}", headers=headers)

    assert response.status_code == 200

    workflow: Workflow = get_workflow_by_trigger_id(trigger_id, db)
    assert workflow is not None
    graph: WorkflowGraph = workflow.data
    assert workflow.trigger_id == trigger_id
    assert graph.root.graph_id == 1
    assert graph.root.id == trigger_id
    assert len(graph.nodes) == 1
    delete_workflow(workflow.id, db)


def test_workflow_triggers_get_all(client, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/workflows/triggers", headers=headers)

    assert response.status_code == 200

    triggers = TRIGGER_REGISTRY.modules.values()
    for trigger in triggers:
        if issubclass(trigger, Module):
            assert trigger.id not in response.text
            continue
        assert trigger.id in response.text


def test_workflow_moduleIndex_get_all(client, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/workflows/moduleIndex/type:all", headers=headers)

    assert response.status_code == 200

    modules = MODULE_REGISTRY.modules.values()
    for module in modules:
        if issubclass(module, Trigger):
            assert module.id not in response.text
            continue
        assert module.id in response.text


def test_workflow_moduleView(client, site_admin_user_token) -> None:
    name = "stop-execution"

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/moduleView/{name}", headers=headers)

    assert response.status_code == 200

    assert name in MODULE_REGISTRY.modules


def test_workflow_toggleModule(client, site_admin_user_token, db, workflows) -> None:
    name = "attribute-after-save"
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/workflows/toggleModule/{name}/1/1", headers=headers)

    assert response.status_code == 200

    db.commit()
    workflow = get_workflow_by_trigger_id(name, db)
    db.refresh(workflow)

    assert workflow is not None
    assert workflow.enabled
    graph: WorkflowGraph = workflow.data
    assert not graph.root.disabled

    headers = {"authorization": site_admin_user_token}
    response2 = client.post(f"/workflows/toggleModule/{name}/0/1", headers=headers)

    assert response2.status_code == 200

    db.commit()
    workflow2 = get_workflow_by_trigger_id(name, db)
    db.refresh(workflow2)

    assert workflow2 is not None
    assert not workflow2.enabled
    graph2: WorkflowGraph = workflow2.data
    assert graph2.root.disabled


def test_workflow_toggleWorkflows(client, site_admin_user_token, db) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/workflows/toggleWorkflows/1", headers=headers)

    assert response.status_code == 200
    workflow_setting_name = "worfklow_feature_enabled"
    db.commit()
    admin_setting_enabled = get_admin_setting(workflow_setting_name, db)
    assert admin_setting_enabled == "True"

    response2 = client.post("/workflows/toggleWorkflows/0", headers=headers)
    assert response2.status_code == 200
    db.commit()
    admin_setting_disabled = get_admin_setting(workflow_setting_name, db)
    assert admin_setting_disabled == "False"


def test_workflow_workflowSetting(client, site_admin_user_token, db) -> None:
    headers = {"authorization": site_admin_user_token}
    assert client.post("/workflows/toggleWorkflows/0", headers=headers).status_code == 200

    response_false = client.get("/workflows/workflowsSetting", headers=headers)
    assert response_false.status_code == 200
    assert response_false.text == "false"

    headers = {"authorization": site_admin_user_token}
    assert client.post("/workflows/toggleWorkflows/1", headers=headers).status_code == 200

    response_true = client.get("/workflows/workflowsSetting", headers=headers)
    assert response_true.status_code == 200
    assert response_true.text == "true"


def get_admin_setting(setting_name: str, db: Session) -> str:
    setting_db = db.execute(select(AdminSetting).where(AdminSetting.setting == setting_name))
    setting: AdminSetting | None = cast(AdminSetting | None, setting_db.scalars().first())
    if setting is None:
        raise Exception()
    return str(setting.value)


def get_workflow_by_trigger_id(
    trigger_id: str,
    db: Session,
) -> Workflow | None:
    result = db.execute(select(Workflow).where(Workflow.trigger_id == trigger_id).limit(1))
    return result.scalars().first()


def delete_workflow(workflow_id: int, db: Session) -> bool:
    workflow: Workflow | None = db.get(Workflow, workflow_id)
    if workflow is None:
        return False
    db.delete(workflow)
    db.commit()
    return True
