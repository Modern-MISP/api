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

from collections.abc import Sequence
from time import time
from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.responses.check_graph_response import CheckGraphResponse
from mmisp.api_schemas.responses.standard_status_response import (
    StandardStatusIdentifiedResponse,
    StandardStatusResponse,
)
from mmisp.api_schemas.workflows import WorkflowEditRequest, WorkflowStatusResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.workflow import Workflow
from mmisp.util.models import update_record
from mmisp.workflows.fastapi import workflow_entity_to_json_dict
from mmisp.workflows.graph import WorkflowGraph
from mmisp.workflows.legacy import GraphFactory

router = APIRouter(tags=["workflows"])


def __create_new_workflow(name: str, description: str, data: dict, trigger_id: str) -> Workflow:
    return Workflow(
        name=name,
        description=description,
        timestamp=time.time(),
        trigger_id=trigger_id,
        data=data,
    )


@router.get(
    "/workflows/index",
    status_code=status.HTTP_200_OK,
    summary="Returns a list of all workflows",
)
async def index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    name: str | None = None,
    uuid: str | None = None,
) -> List[dict]:
    """
    Returns a list of all workflows.

    - **name**: Filter by workflow name.
    - **uuid**: Filter by workflow UUID.

    Filters can be applied, mainly filters for a name or a uuid.
    """
    result = await db.execute(select(Workflow))
    workflows: Sequence[Workflow] = result.scalars().all()

    result: List[Dict[str, str]] = []

    for workflow in workflows:
        json = workflow_entity_to_json_dict(workflow)
        result.append(json)

    return result


@router.post("/workflows/edit/{workflowId}", status_code=status.HTTP_200_OK, summary="Edits a workflow")
async def edit(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
    request: WorkflowEditRequest,
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
    new_data = {
        "name": request.workflow_name,
        "description": request.workflow_description,
        "graph": GraphFactory.jsondict2graph(request.workflow_graph),
    }

    workflow: Workflow | None = await db.get(Workflow, workflow_id)

    if not workflow:
        workflow = Workflow()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    else:
        update_record(workflow, new_data)
        await db.commit()
        await db.refresh(workflow)

    return workflow_entity_to_json_dict(workflow)


@router.delete("/workflows/delete/{workflowId}", status_code=status.HTTP_200_OK, summary="Deletes a workflow")
async def delete(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> StandardStatusIdentifiedResponse:
    """
    Deletes a workflow. It will be removed from the database.

    - **workflow_id** The ID of the workflow to delete.
    """
    workflow: Workflow = await db.get(Workflow, workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=WorkflowStatusResponse(
                name="Invalid Workflow.", message="Invalid Workflow.", url=f"/workflows/delete/{workflow_id}"
            ).dict(),
        )

    await db.delete(workflow)
    await db.commit()

    return WorkflowStatusResponse(
        saved=True,
        success=True,
        message="Workflow deleted.",
        name="Workflow deleted.",
        url=f"/workflows/delete/{workflow_id}",
        id=workflow_id,
    )


@router.get(
    "/workflows/view/{workflowId}",
    status_code=status.HTTP_200_OK,
    summary="Get a workflow",
    description="",
)
async def view(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> Dict[str, Any]:
    """
    Gets a workflow.

    Is called view because it is used to display the workflow in the visual editor
    but it just returns the data of a workflow.

    - **workflow_id** The ID of the workflow to view.

    """
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id).limit(1))
    workflow: Workflow = result.scalars().first()
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=WorkflowStatusResponse(
                name="Invalid Workflow.",
                message="Invalid Workflow.",
                url=f"/workflows/view/{workflow_id}",
            ).dict(),
        )
    return workflow_entity_to_json_dict(workflow)


@router.post("/workflows/executeWorkflow/{workflowId}", status_code=status.HTTP_200_OK, summary="Executes a workflow")
async def executeWorkflow(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> StandardStatusResponse:
    """
    Executes a workflow.

    Is used for debugging.

    - **workflow_id** The ID of the workflow to execute.
    """
    return StandardStatusResponse(
        saved=True, success=True, message="Nothing happened, just a mockup", name="Test", url="https://example.com"
    )


@router.get("/workflows/triggers", status_code=status.HTTP_200_OK, summary="Returns a list with all triggers")
async def triggers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    scope: Optional[str],
    enabled: Optional[bool],
    blocking: Optional[bool],
    limit: Optional[int],
    page: Optional[int],
) -> List[Dict[str, str]]:
    """
    Returns a list with triggers.

    A trigger starts a workflow. It is used for the trigger overview page.

    - **scope** Filters for the scope of the triggers (attribute, event, log etc.)
    - **enabled** Filters whether the trigger is enabled/ disabled
    - **blocking** Filters for blocking/ non-blocking triggers
    - **limit**: The number of items to display per page (for pagination).
    - **page**: The page number to display (for pagination).
    """
    return {{}}


@router.get("/workflows/moduleIndex", status_code=status.HTTP_200_OK, summary="Returns modules")
async def moduleIndex(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    enabled: Optional[bool],
    limit: Optional[int],
    page: Optional[int],
    type: str = "action",
    actiontype: str = "all",
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
    return {{}}


@router.get("/workflows/moduleView/{moduleId}", status_code=status.HTTP_200_OK, summary="Returns a singular module")
async def moduleView(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    module_id: Annotated[int, Path(alias="moduleId")],
) -> Dict[str, Any]:
    """
    Returns a singular module.

    - **module_id** The ID of the module.
    """
    return {}


@router.post(
    "/workflows/toggleModule/{moduleId}/{enable}", status_code=status.HTTP_200_OK, summary="Enables/ disables a module"
)
async def toggleModule(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    module_id: Annotated[int, Path(alias="moduleId")],
    enable: Annotated[bool, Path(alias="enable")],
    is_trigger: Optional[bool] = False,
) -> StandardStatusResponse:
    """
    Enables/ disables a module. Respons with a success status.

    Disabled modules can't be used in the visual editor.

    - **module_id**: The ID of the module.
    - **enable**: Whether the module should be enabled or not.
    - **is_trigger**: Indicates if the module is a trigger module.
    Trigger modules have specific behaviors and usage within the system.
    """
    return StandardStatusResponse(
        saved=True, success=True, message="Nothing happened, just a mockup", name="Test", url="https://example.com"
    )


@router.post("/workflows/checkGraph", status_code=status.HTTP_200_OK, summary="Checks if the given graph is correct")
async def checkGraph(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_graph: Annotated[WorkflowGraph, Depends(GraphFactory.jsondict2graph)],
) -> CheckGraphResponse:
    """
    Checks if the given graph is correct.

    This will check if the graph is acyclic, if any node has multiple output connections
    and if there are path warnings.

    - **graph** The workflow graph to check.
    """
    return CheckGraphResponse()


@router.post(
    "/workflows/toggleWorkflows", status_code=status.HTTP_200_OK, summary="Enable/ disable the workflow feature"
)
async def toggleWorkflows(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> StandardStatusResponse:
    """
    Enable/ disable the workflow feature. Respons with a success status.

    Globally enables/ disables the workflow feature in your MISP instance.
    """
    return StandardStatusResponse(
        saved=True, success=True, message="Nothing happened, just a mockup", name="Test", url="https://example.com"
    )
