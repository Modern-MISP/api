"""
This API endpoint (`workflow.py`) is designed for interacting with workflows.
It supports fundamental operations such as editing, deleting, and getting workflows,
along with validating workflow graphs.

Moreover, it includes endpoints for managing modules,
such as listing them and enabling/disabling their functionalities.

These operations require database access, relying on `get_db()`.
Authorization is essential for all actions, enforced via `authorize(AuthStrategy.HYBRID)`.

Responses from these endpoints are consistently formatted in JSON,
providing detailed information about each operation's outcome.
"""

import time
from collections.abc import Sequence
from json import loads
from typing import Annotated, Any, Dict, List, cast

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)
from sqlalchemy.future import select
from starlette.requests import (
    Request,
)

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.responses.check_graph_response import (
    CheckGraphResponse,
)
from mmisp.api_schemas.responses.standard_status_response import (
    StandardStatusIdentifiedResponse,
    StandardStatusResponse,
    StandartResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.admin_setting import AdminSetting
from mmisp.db.models.workflow import Workflow
from mmisp.lib.logger import alog, log
from mmisp.workflows.fastapi import (
    module_entity_to_json_dict,
    trigger_entity_to_json_dict,
    workflow_entity_to_json_dict,
)
from mmisp.workflows.graph import (
    Apperance,
    Graph,
    WorkflowGraph,
)
from mmisp.workflows.legacy import (
    GraphFactory,
    GraphValidation,
)
from mmisp.workflows.modules import (
    NODE_REGISTRY,
    Module,
    ModuleAction,
    ModuleConfiguration,
    ModuleLogic,
    Trigger,
)

from ..error import LegacyMISPCompatibleHTTPException

router = APIRouter(tags=["workflows"])


@router.get(
    "/workflows/index",
    status_code=status.HTTP_200_OK,
    summary="Returns a list of all workflows",
)
@alog
async def index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> List[dict]:
    """
    Returns a list of all workflows in the JSON format.
    """
    workflows = await query_all_workflows(db)

    result: List[dict] = []
    for workflow in workflows:
        json = workflow_entity_to_json_dict(workflow)
        result.append(json)

    return result


@alog
async def query_all_workflows(db: Session) -> Sequence[Workflow]:
    db_result = await db.execute(select(Workflow))
    workflows: Sequence[Workflow] = db_result.scalars().all()
    return workflows


@router.post(
    "/workflows/edit/{workflowId}",
    status_code=status.HTTP_200_OK,
    summary="Edits a workflow",
)
@alog
async def edit(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
    request: Request,
) -> Dict[str, Any]:
    """
    Edits a workflow.

    When a change it made this endpoints overrwrites the outdated workflow in the database.
    It is also used to add new workflows. The response is the edited workflow.

    - **workflow_id** The ID of the workflow to edit.
    - **workflow_name** The new name.
    - **workflow_description** The new description.
    - **workflow_graph** The new workflow graph.
    """

    # Forms conversion to useable data
    form_data = await request.form()

    data = loads(str(form_data["data[Workflow][data]"]))

    workflow = await edit_workflow(
        workflow_id=workflow_id,
        db=db,
        name=str(form_data["data[Workflow][name]"]),
        description=str(form_data["data[Workflow][description]"]),
        data=GraphFactory.jsondict2graph(data),
    )
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return workflow_entity_to_json_dict(workflow)


@alog
async def edit_workflow(
    workflow_id: int,
    db: Session,
    name: str,
    description: str,
    data: Graph,
) -> Workflow | None:
    workflow: Workflow | None = await db.get(Workflow, workflow_id)

    if not workflow:
        return None

    new_data = {
        "name": name,
        "description": description,
        "data": data,
    }

    workflow.patch(**new_data)
    await workflow.data.initialize_graph_modules(db)
    result = workflow.data.check()
    if not result.is_valid():
        report = GraphValidation.report_as_str(result, workflow.data)
        raise LegacyMISPCompatibleHTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            message=f"Refusing to save invalid graph:\n{report}",
        )
    await db.flush()
    await db.refresh(workflow)
    return workflow


@router.delete(
    "/workflows/delete/{workflowId}",
    status_code=status.HTTP_200_OK,
    summary="Deletes a workflow",
)
@alog
async def delete(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> StandardStatusIdentifiedResponse:
    """
    Deletes a workflow. It will be removed from the database.

    - **workflow_id** The ID of the workflow to delete.
    """
    success = await delete_workflow(workflow_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=StandartResponse(
                name="Invalid Workflow.", message="Invalid Workflow.", url=f"/workflows/delete/{workflow_id}"
            ).model_dump(),
        )

    return StandardStatusIdentifiedResponse(
        saved=success,
        success=success,
        message="Workflow deleted.",
        name="Workflow deleted.",
        url=f"/workflows/delete/{workflow_id}",
        id=workflow_id,
    )


@alog
async def delete_workflow(workflow_id: int, db: Session) -> bool:
    workflow = await get_workflow_by_id(workflow_id, db)
    if workflow is None:
        return False
    await db.delete(workflow)
    await db.flush()
    return True


@router.get(
    "/workflows/view/{workflowId}",
    status_code=status.HTTP_200_OK,
    summary="Get a workflow",
    description="",
)
@alog
async def view(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> Dict[str, Any]:
    """
    Gets a workflow.

    Is called view because it is used to display the workflow in the visual editor
    but it just returns the data of a workflow.

    - **workflow_id** The ID of the workflow to view.

    """
    workflow: Workflow | None = await get_workflow_by_id(workflow_id, db)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=StandartResponse(
                name="Invalid Workflow.",
                message="Invalid Workflow.",
                url=f"/workflows/view/{workflow_id}",
            ).model_dump(),
        )

    await workflow.data.initialize_graph_modules(db)

    return workflow_entity_to_json_dict(workflow)


@alog
async def get_workflow_by_id(workflow_id: int, db: Session) -> Workflow | None:
    return await db.get(Workflow, workflow_id)


@router.post(
    "/workflows/editor/{triggerId}",
    status_code=status.HTTP_200_OK,
    summary="Creates a new workflow",
)
@alog
async def editor(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    trigger_id: Annotated[str, Path(alias="triggerId")],
) -> StandartResponse:
    """
    Creates a new workflow.
    In MISP this loaded the editor and send the editor HTML.
    But it also created a workflow if you tried to edit a not-existing workflow.
    We use is ONLY for creating, because we don't need the rest.

    - **workflow_id** The ID of the workflow to create.
    """
    workflow = await get_workflow_by_trigger_id(trigger_id, db)
    if workflow is None:
        await create_workflow(trigger_id, db)
        return StandartResponse(
            name="Created workflow.",
            message="Created workflow.",
            url=f"/workflows/editor/{trigger_id}",
        )
    else:
        return StandartResponse(
            name="Workflow already exists.",
            message="Workflow already exists.",
            url=f"/workflows/editor/{trigger_id}",
        )


@alog
async def create_workflow(trigger_id: str, db: Session) -> None:
    new_workflow = __create_new_workflow_object(
        name=f"Workflow for trigger {trigger_id}",
        trigger_id=trigger_id,
    )

    db.add(new_workflow)
    await db.flush()
    await db.refresh(new_workflow)


@log
def __create_new_workflow_object(name: str, trigger_id: str, description: str = "") -> Workflow:
    nt = NODE_REGISTRY.triggers[trigger_id]

    new_trigger = nt(
        id=nt.id,
        name=nt.name,
        blocking=nt.blocking,
        scope=nt.scope,
        overhead=nt.overhead,
        apperance=Apperance((0.0, 0.0), False, "block-type-trigger", "1"),
        graph_id=1,
        inputs={},
        outputs={},
    )
    new_graph = WorkflowGraph(
        root=new_trigger,
        nodes={
            1: new_trigger,
        },
        frames={},
    )

    return Workflow(
        name=name,
        description=description,
        timestamp=int(time.time()),
        trigger_id=trigger_id,
        data=new_graph,
    )


@router.post(
    "/workflows/executeWorkflow/{workflowId}",
    status_code=status.HTTP_200_OK,
    summary="Executes a workflow",
)
@alog
async def executeWorkflow(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> StandardStatusResponse:
    """
    Executes a workflow.

    Is used for debugging.

    - **workflow_id** The ID of the workflow to execute.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get(
    "/workflows/triggers",
    status_code=status.HTTP_200_OK,
    summary="Returns a list with all triggers",
)
@alog
async def triggers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> List[Dict[str, Any]]:
    """
    Returns a list with triggers.

    A trigger starts a workflow. It is used for the trigger overview page.

    - **scope** Filters for the scope of the triggers (attribute, event, log etc.)
    - **enabled** Filters whether the trigger is enabled/ disabled
    - **blocking** Filters for blocking/ non-blocking triggers
    - **limit**: The number of items to display per page (for pagination).
    - **page**: The page number to display (for pagination).
    """
    all_triggers = NODE_REGISTRY.triggers.values()

    result = []

    # too ugly to get it's own function :(
    for type_trigger in all_triggers:
        trigger = cast(Trigger, type_trigger)
        disabled = True
        workflow_json = {}
        # needs to query the corresponding workflow for the trigger to get the disabled field :(
        workflow = await get_workflow_by_trigger_id(trigger.id, db)
        if workflow:
            workflow_json = workflow_entity_to_json_dict(workflow)["Workflow"]
            data = cast(WorkflowGraph, workflow.data)
            disabled = cast(Trigger, data.root).disabled
        json = trigger_entity_to_json_dict(trigger, workflow_json, disabled)
        result.append(json)

    return result


@alog
async def get_workflow_by_trigger_id(
    trigger_id: str,
    db: Session,
) -> Workflow | None:
    result = await db.execute(select(Workflow).where(Workflow.trigger_id == trigger_id).limit(1))
    return result.scalars().first()


@router.get("/workflows/moduleIndex/type:{type}", status_code=status.HTTP_200_OK, summary="Returns modules")
@alog
async def moduleIndex(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    type: Annotated[str, Path()],
) -> List[Dict[str, Any]]:
    """
    Retrieve modules with optional filtering.

    All filter parameters are optional. If no parameters are provided, no filtering will be applied.

    - **type**: Filter by type. Valid values are 'action', 'logic', 'custom', and 'all'.
    - **actiontype**: Filter by action type. Valid values are 'all', 'mispmodule', and 'blocking'.
    - **enabled**: If true, returns only enabled modules. If false, returns only disabled modules.
    - **limit**: The number of items to display per page (for pagination).
    - **page**: The page number to display (for pagination).
    """
    all_modules = NODE_REGISTRY.all().values()

    response: List[dict] = []

    for module in all_modules:
        # FIXME modules/triggers are in both registries now. This is wrong
        # and should be fixed in lib properly. Band-aid fix here.
        if issubclass(module, Trigger):
            continue
        instance = cast(Module, __create_module_or_trigger_object(module))
        if __filter_index_modules(instance, type):
            await instance.initialize_for_visual_editor(db)
            module_json = module_entity_to_json_dict(instance)
            response.append(module_json)

    return response


@log
def __create_module_or_trigger_object(module: type[Module | Trigger]) -> Module | Trigger:
    # FIXME it's a little hacky, but we initialize `apperance` into
    # None because it's nowhere used when returning module-data only.
    if issubclass(module, Trigger):
        return module(inputs={}, outputs={}, graph_id=0, apperance=None)  # type:ignore[call-arg,arg-type]
    return module(
        configuration=ModuleConfiguration({}),
        inputs={},
        outputs={},
        graph_id=0,
        apperance=None,  # type:ignore[call-arg,arg-type]
        on_demand_filter=None,
    )


@log
def __filter_index_modules(module: Module, type: str) -> bool:
    if type == "action" and not isinstance(module, ModuleAction):
        return False
    if type == "logic" and not isinstance(module, ModuleLogic):
        return False

    return True


@router.get(
    "/workflows/moduleView/{moduleId}",
    status_code=status.HTTP_200_OK,
    summary="Returns a singular module",
)
@alog
async def moduleView(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    module_id: Annotated[str, Path(alias="moduleId")],
) -> Dict[str, Any]:
    """
    Returns a singular module.

    - **module_id** The ID of the module.
    """

    all_modules = NODE_REGISTRY.all().values()

    for module in all_modules:
        if module.id == module_id:
            instance = __create_module_or_trigger_object(module)
            if isinstance(instance, Module):
                await instance.initialize_for_visual_editor(db)
            return module_entity_to_json_dict(instance)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=StandartResponse(
            name="Invalid trigger ID",
            message="Invalid trigger ID",
            url=f"/workflows/moduleView/{module_id}",
        ).model_dump(),
    )


@router.post(
    "/workflows/toggleModule/{nodeId}/{enable}/{isTrigger}",
    status_code=status.HTTP_200_OK,
    summary="Enables/ disables a module",
)
@alog
async def toggleModule(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    node_id: Annotated[str, Path(alias="nodeId")],
    enable: Annotated[bool, Path(alias="enable")],
    is_trigger: Annotated[bool, Path(alias="isTrigger")],
) -> StandartResponse:
    """
    Enables/ disables a module. Respons with a success status.

    Disabled modules can't be used in the visual editor.

    Note that the legacy misp accepted all node ID's and never threw an error.

    - **module_id**: The ID of the module.
    - **enable**: Whether the module should be enabled or not.
    - **is_trigger**: Indicates if the module is a trigger module.
    Trigger modules have specific behaviors and usage within the system.
    """

    if not is_trigger:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )

    # this does not exist in legacy misp, they just accept every node ID
    workflow: Workflow | None = await get_workflow_by_trigger_id(node_id, db)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=StandartResponse(
                name="Invalid trigger ID",
                message="Invalid trigger ID",
                url=f"/workflows/toggleModule/{node_id}/{enable}/{is_trigger}",
            ).model_dump(),
        )

    # probaby a stupid way to create a new graph but whitout this (the code below) it won't work
    # ugly hack :(
    # graph: WorkflowGraph = workflow.data.root.disabled = not enable

    graph_json = GraphFactory.graph2jsondict(cast(WorkflowGraph, workflow.data))
    graph_json["1"]["data"]["disabled"] = not enable
    graph = GraphFactory.jsondict2graph(graph_json)

    workflow.data = cast(WorkflowGraph, graph)
    workflow.enabled = enable

    await db.flush()
    await db.refresh(workflow)
    enabled_text = "Enabled" if (enable) else "Disabled"
    return StandardStatusResponse(
        saved=True,
        success=True,
        message=f"{enabled_text} module {node_id}",
        name=f"{enabled_text} module {node_id}",
        url=f"/workflows/toggle_module/{node_id}",
    )


@router.post(
    "/workflows/checkGraph",
    status_code=status.HTTP_200_OK,
    summary="Checks if the given graph is correct",
)
@alog
async def checkGraph(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    request: Request,  # 'Request' because it gets form data from the frontend.
) -> CheckGraphResponse:
    """
    Checks if the given graph is correct.

    This will check if the graph is acyclic, if any node has multiple output connections
    and if there are path warnings.

    - **graph** The workflow graph to check.
    """
    form_data = await request.form()
    data = loads(str(form_data["graph"]))
    graph = GraphFactory.jsondict2graph(data)
    await graph.initialize_graph_modules(db)

    result = graph.check()
    return GraphValidation.report(result)


@router.post(
    "/workflows/toggleWorkflows/{enabled}",
    status_code=status.HTTP_200_OK,
    summary="Enable/ disable the workflow feature",
)
@alog
async def toggleWorkflows(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    enabled: Annotated[bool, Path(alias="enabled")],
) -> StandardStatusResponse:
    """
    Enable/ disable the workflow feature. Respons with a success status.

    Globally enables/ disables the workflow feature in your MISP instance, not a single workflow.
    A single workflow is enabled through it's corresponding trigger.
    """
    await set_admin_setting(workflow_setting_name, str(enabled), db)
    return StandardStatusResponse(
        saved=True,
        success=True,
        message=f"Workflows globally enabled: {enabled}",
        name=f"Workflows globally enabled: {enabled}",
        url=f"/workflows/toggleWorkflows/{enabled}",
    )


# find better place to store that
workflow_setting_name = "workflow_feature_enabled"


# Should be moved to lib
@alog
async def set_admin_setting(setting_name: str, value: str, db: Session) -> None:
    setting_db = await db.execute(select(AdminSetting).where(AdminSetting.setting == setting_name))
    setting: AdminSetting | None = setting_db.scalars().first()

    if setting is None:
        new_setting = AdminSetting(setting=setting_name, value=value)
        db.add(new_setting)
        await db.flush()
        await db.refresh(new_setting)
        return

    setting.value = value
    await db.flush()
    await db.refresh(setting)


@alog
async def get_admin_setting(setting_name: str, db: Session) -> str:
    setting_db = await db.execute(select(AdminSetting).where(AdminSetting.setting == setting_name))
    setting: AdminSetting | None = cast(AdminSetting | None, setting_db.scalars().first())
    if setting is None:
        return "False"
    return str(setting.value)


@router.get(
    "/workflows/workflowsSetting",
    status_code=status.HTTP_200_OK,
    summary="Status whether the workflow setting is globally enabled/ disabled",
)
@alog
async def workflowsSetting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> bool:
    """
    Returns whether the workflows are globally enabled/ disabled.
    """
    value = await get_admin_setting(workflow_setting_name, db)
    return value == "True"


@router.post(
    "/workflows/debugToggleField/{workflowId}/{enabled}",
    status_code=status.HTTP_200_OK,
    summary="Status whether the workflow setting is globally enabled/ disabled",
)
@alog
async def debugToggleField(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
    enabled: Annotated[bool, Path(alias="enabled")],
) -> StandardStatusIdentifiedResponse:
    success = await toggleWorkflowDebugField(workflow_id, enabled, db)
    enabled_string = "Enabled" if success else "Disabled"
    return StandardStatusIdentifiedResponse(
        saved=success,
        success=success,
        name=f"{enabled_string} debug mode",
        message=f"{enabled_string} debug mode",
        # toggle_debug is from old MISP, even though the 'workflows/debugToggleField' endpoint is called
        url=f"/workflows/toggle_debug/{workflow_id}",
        id=f"{workflow_id}",
    )


@alog
async def toggleWorkflowDebugField(workflow_id: int, debug_enabled: bool, db: Session) -> bool:
    workflow = await get_workflow_by_id(workflow_id, db)
    if workflow is None:
        return False
    workflow.debug_enabled = debug_enabled
    await db.flush()
    await db.refresh(workflow)
    return True
