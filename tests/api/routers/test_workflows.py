import json
from collections.abc import Sequence
from typing import List, cast

import pytest
import pytest_asyncio
from sqlalchemy.future import select

from mmisp.api_schemas.responses.check_graph_response import CheckGraphResponse
from mmisp.db.database import Session
from mmisp.db.models.admin_setting import AdminSetting
from mmisp.db.models.workflow import Workflow
from mmisp.tests.generators.model_generators.workflow_generator import (
    generate_workflows,
    genrerate_workflow_with_id,
)
from mmisp.workflows.graph import WorkflowGraph
from mmisp.workflows.legacy import GraphFactory
from mmisp.workflows.modules import NODE_REGISTRY, Module, Trigger


@pytest_asyncio.fixture
async def workflows(db):
    workflows: List[Workflow] = generate_workflows()
    workflows.append(genrerate_workflow_with_id(50))

    for workflow in workflows:
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)

    yield workflows

    for workflow in workflows:
        await db.delete(workflow)
        await db.commit()


@pytest.mark.asyncio
async def test_workflows_index(db, site_admin_user_token, client, workflows) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/workflows/index", headers=headers)

    result = await db.execute(select(Workflow))
    workflows: Sequence[Workflow] = result.scalars().all()

    json_dict = json.loads(response.content.decode())

    for count in range(0, len(workflows)):
        db_workflow = workflows[count]
        response_workflow = json_dict[count]["Workflow"]
        assert str(db_workflow.id) == response_workflow["id"]
        assert db_workflow.uuid == response_workflow["uuid"]


@pytest.mark.asyncio
async def test_workflow_edit_edit_existing(db, site_admin_user_token, client) -> None:
    id: int = 50
    headers = {
        "authorization": site_admin_user_token,
        "accept": "application/json",
    }

    new_workflow = genrerate_workflow_with_id(id)
    db.add(new_workflow)
    await db.commit()
    await db.refresh(new_workflow)
    data = json.dumps(GraphFactory.graph2jsondict(new_workflow.data))

    payload = {
        "data[Workflow][name]": "new workflow name",
        "data[Workflow][description]": "new workflow description",
        "data[Workflow][data]": data,
    }
    response = client.post(f"/workflows/edit/{id}", headers=headers, data=payload)

    assert response.status_code == 200

    workflow: Workflow = await db.get(Workflow, id)
    await db.commit()
    await db.refresh(new_workflow)
    workflow_dict = json.loads(response.content.decode())["Workflow"]
    assert workflow_dict["name"] == payload["data[Workflow][name]"]
    assert workflow_dict["description"] == payload["data[Workflow][description]"]
    assert workflow_dict["data"] == json.loads(data)
    assert workflow.name == payload["data[Workflow][name]"]
    assert workflow.description == payload["data[Workflow][description]"]
    assert workflow.data.nodes == new_workflow.data.nodes
    assert workflow.data.root == new_workflow.data.root
    assert list(workflow.data.frames) == list(new_workflow.data.frames)

    await db.delete(new_workflow)
    await db.commit()


@pytest.mark.asyncio
async def test_check_graph(db, site_admin_user_token, client):
    id: int = 50
    headers = {
        "authorization": site_admin_user_token,
        "accept": "application/json",
    }

    new_workflow = genrerate_workflow_with_id(id)
    db.add(new_workflow)
    await db.commit()
    await db.refresh(new_workflow)
    data = json.dumps(GraphFactory.graph2jsondict(new_workflow.data))

    payload = {
        "graph": data,
    }
    response = client.post("/workflows/checkGraph", headers=headers, data=payload)

    assert response.status_code == 200
    check_graph_json = json.loads(response.text)
    check_graph_response: CheckGraphResponse = CheckGraphResponse(**check_graph_json)
    assert check_graph_response.is_acyclic.is_acyclic
    assert not check_graph_response.multiple_output_connection.has_multiple_output_connection
    assert not check_graph_response.path_warnings.has_path_warnings
    assert check_graph_response.unsupported_modules == []
    await db.delete(new_workflow)
    await db.commit()


@pytest.mark.asyncio
async def test_edit_workflow_invalid(site_admin_user_token, client, workflows) -> None:
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


@pytest.mark.asyncio
async def test_workflow_view(client, site_admin_user_token, workflows) -> None:
    id: int = 50
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/view/{id}", headers=headers)

    assert response.status_code == 200
    workflow_dict = json.loads(response.content.decode())["Workflow"]
    assert workflow_dict["id"] == str(id)
    assert workflow_dict["name"] == "Workflow for testing"
    assert workflow_dict["data"]["1"]["class"] == "block-type-trigger"


@pytest.mark.asyncio
async def test_workflow_view_invalid_id(db, client, site_admin_user_token) -> None:
    id: int = 200
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/view/{id}", headers=headers)

    db_result = await db.execute(select(Workflow).where(Workflow.id == id))
    workflow: Workflow = db_result.scalars().first()

    assert response.status_code == 404
    assert workflow is None
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["detail"]["name"] == "Invalid Workflow."
    assert detail_dict["detail"]["message"] == "Invalid Workflow."
    assert detail_dict["detail"]["url"] == f"/workflows/view/{id}"


@pytest.mark.asyncio
async def test_workflow_delete_success(client, site_admin_user_token, db) -> None:
    id: int = 150
    workflow = genrerate_workflow_with_id(id)
    db.add(workflow)
    await db.commit()

    workflow = await db.get(Workflow, id)

    assert isinstance(workflow, Workflow)
    assert workflow.id == id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/workflows/delete/{id}", headers=headers)

    db.expire(workflow)
    workflow2 = await db.get(Workflow, id)

    assert response.status_code == 200
    assert workflow2 is None
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["saved"]
    assert detail_dict["success"]
    assert detail_dict["name"] == "Workflow deleted."
    assert detail_dict["message"] == "Workflow deleted."
    assert detail_dict["url"] == f"/workflows/delete/{id}"
    assert detail_dict["id"] == id


@pytest.mark.asyncio
async def test_workflow_delete_invalid_id(client, site_admin_user_token, db) -> None:
    id: int = 200
    db_result = await db.execute(select(Workflow).where(Workflow.id == id))
    workflow: Workflow = db_result.scalars().first()

    assert workflow is None

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/workflows/delete/{id}", headers=headers)

    await db.commit()

    db_result2 = await db.execute(select(Workflow).where(Workflow.id == id))
    workflow2: Workflow = db_result2.scalars().first()

    assert response.status_code == 404
    assert workflow2 is None
    assert str(id) in response.text
    detail_dict = json.loads(response.content.decode())
    assert detail_dict["detail"]["name"] == "Invalid Workflow."
    assert detail_dict["detail"]["message"] == "Invalid Workflow."
    assert detail_dict["detail"]["url"] == f"/workflows/delete/{id}"


@pytest.mark.asyncio
async def test_workflow_editor_create_new_workflow(client, site_admin_user_token, db) -> None:
    trigger_id = "attribute-after-save"
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/workflows/editor/{trigger_id}", headers=headers)

    assert response.status_code == 200

    workflow: Workflow = await get_workflow_by_trigger_id(trigger_id, db)
    assert workflow is not None
    graph: WorkflowGraph = workflow.data
    assert workflow.trigger_id == trigger_id
    assert graph.root.graph_id == 1
    assert graph.root.id == trigger_id
    assert len(graph.nodes) == 1
    await delete_workflow(workflow.id, db)


@pytest.mark.asyncio
async def test_workflow_triggers_get_all(client, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/workflows/triggers", headers=headers)

    assert response.status_code == 200

    triggers = NODE_REGISTRY.all().values()
    for trigger in triggers:
        if issubclass(trigger, Module):
            assert trigger.id not in response.text
            continue
        assert trigger.id in response.text


@pytest.mark.asyncio
async def test_workflow_moduleIndex_get_all(client, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/workflows/moduleIndex/type:all", headers=headers)

    assert response.status_code == 200

    modules = NODE_REGISTRY.all().values()
    print(modules)
    for module in modules:
        if issubclass(module, Trigger):
            assert module.id not in response.text
            continue
        assert module.id in response.text


@pytest.mark.asyncio
async def test_workflow_moduleView(client, site_admin_user_token) -> None:
    name = "stop-execution"

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/workflows/moduleView/{name}", headers=headers)

    assert response.status_code == 200

    assert name in NODE_REGISTRY.all()


@pytest.mark.asyncio
async def test_workflow_toggleModule(client, site_admin_user_token, db, workflows) -> None:
    name = "attribute-after-save"
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/workflows/toggleModule/{name}/1/1", headers=headers)

    assert response.status_code == 200

    await db.commit()
    workflow = await get_workflow_by_trigger_id(name, db)
    await db.refresh(workflow)

    assert workflow is not None
    assert workflow.enabled
    graph: WorkflowGraph = workflow.data
    assert not graph.root.disabled

    headers = {"authorization": site_admin_user_token}
    response2 = client.post(f"/workflows/toggleModule/{name}/0/1", headers=headers)

    assert response2.status_code == 200

    await db.commit()
    workflow2 = await get_workflow_by_trigger_id(name, db)
    await db.refresh(workflow2)

    assert workflow2 is not None
    assert not workflow2.enabled
    graph2: WorkflowGraph = workflow2.data
    assert graph2.root.disabled


@pytest.mark.asyncio
async def test_workflow_toggleWorkflows(client, site_admin_user_token, db) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/workflows/toggleWorkflows/1", headers=headers)

    assert response.status_code == 200
    workflow_setting_name = "workflow_feature_enabled"
    await db.commit()
    admin_setting_enabled = await get_admin_setting(workflow_setting_name, db)
    assert admin_setting_enabled == "True"

    response2 = client.post("/workflows/toggleWorkflows/0", headers=headers)
    assert response2.status_code == 200
    await db.commit()
    admin_setting_disabled = await get_admin_setting(workflow_setting_name, db)
    assert admin_setting_disabled == "False"


@pytest.mark.asyncio
async def test_workflow_workflowSetting(client, site_admin_user_token) -> None:
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


@pytest.mark.asyncio
async def test_workflow_debugToggle(client, site_admin_user_token, db, workflows) -> None:
    id: int = 50
    headers = {"authorization": site_admin_user_token}
    assert client.post(f"/workflows/debugToggleField/{id}/0", headers=headers).status_code == 200

    workflow_disabled: Workflow | None = await db.get(Workflow, id)
    assert workflow_disabled is not None
    assert not workflow_disabled.debug_enabled

    headers = {"authorization": site_admin_user_token}
    assert client.post(f"/workflows/debugToggleField/{id}/1", headers=headers).status_code == 200

    await db.commit()
    workflow_enabled: Workflow | None = await db.get(Workflow, id)
    await db.refresh(workflow_enabled)

    assert workflow_enabled is not None
    assert workflow_enabled.debug_enabled


async def get_admin_setting(setting_name: str, db: Session) -> str:
    setting_db = await db.execute(select(AdminSetting).where(AdminSetting.setting == setting_name))
    setting: AdminSetting | None = cast(AdminSetting | None, setting_db.scalars().first())
    if setting is None:
        raise Exception()
    return str(setting.value)


async def get_workflow_by_trigger_id(
    trigger_id: str,
    db: Session,
) -> Workflow | None:
    result = await db.execute(select(Workflow).where(Workflow.trigger_id == trigger_id).limit(1))
    return result.scalars().first()


async def delete_workflow(workflow_id: int, db: Session) -> bool:
    workflow: Workflow | None = await db.get(Workflow, workflow_id)
    if workflow is None:
        return False
    await db.delete(workflow)
    await db.commit()
    return True
