from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Path, status

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.api_schemas.workflow_response import CheckGraphResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.workflows import Workflow
from mmisp.workflows import Module, Trigger, WorkflowGraph

router = APIRouter(tags=["workflows"])


@router.get(
    "/workflows/index",
    status_code=status.HTTP_200_OK,
    summary="Returns a list of all workflows",
)
async def index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    # TODO: Filters
    # TODO: QuickFilters
) -> List[Workflow]:
    """
    Returns a list of all workflows.

    Filters can be applied, mainly filters for a name or a uuid.
    """
    return []


@router.post("/workflows/edit/{workflowId}", status_code=status.HTTP_200_OK, summary="Edits a workflow")
async def edit(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
    workflow_name: str,
    workflow_description: str,
    workflow_graph: WorkflowGraph,
) -> Workflow:
    """
    Edits a workflow.

    - **workflow_id** the id of the workflow to edit
    - **workflow_name** the new name
    - **workflow_description** the new description
    - **workflow_graph** the new workflow graph \n
    When a change it made this endpoints overrwrites the outdated workflow in the database.
    The response is the edited workflow.
    """
    return Workflow()


@router.delete(
    "/workflows/delete/{workflowId}",
    status_code=status.HTTP_200_OK,
    summary="Deletes a workflow",
    description="Deletes a workflow. It will be removed from the database.",
)
async def delete(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> None:
    """
    Deletes a workflow.

    - **workflow_id** the id of the workflow to delete.
    """
    return None


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
) -> Workflow:
    """
    Gets a workflow.

    - **workflow_id** the id of the workflow to view. \n
    Is called view because it is used to display the workflow in the visual editor
    but it just returns the data of a workflow.
    """
    return Workflow()


@router.post("/workflows/executeWorkflow/{workflowId}", status_code=status.HTTP_200_OK, summary="Executes a workflow")
async def executeWorkflow(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    workflow_id: Annotated[int, Path(alias="workflowId")],
) -> None:
    """
    Executes a workflow.

    - **workflow_id** the id of the workflow to execute. \n
    Is used for debugging.
    """
    return None


@router.get("/workflows/triggers", status_code=status.HTTP_200_OK, summary="Returns a list with all triggers")
async def triggers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> List[Trigger]:
    """
    Returns a list with all triggers.

    Returns a list with all triggers. A trigger starts a workflow.
    It is used for the trigger overview page.
    """
    return []


@router.get(
    "/workflows/moduleIndex",
    status_code=status.HTTP_200_OK,
    summary="Returns modules",
    description="With type:all you can querry all modules. Filters can be applied.",
)
async def moduleIndex(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    # TODO: Add all filter parameters
    # type: ["all", "custom"]
    # actiontype: ["mispmodule", "blocking"]
    enabled: Optional[bool],
) -> List[Module]:
    """
    Returns modules.

    All filter parameters are optional. No parameter means no filtering.
    - **enabled** If this is true/false, it only return enabled/disabled modules.
    """
    return []


@router.get("/workflows/moduleView/{moduleId}", status_code=status.HTTP_200_OK, summary="Returns a singular module")
async def moduleView(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    module_id: Annotated[int, Path(alias="moduleId")],
) -> Module:
    """
    Returns a singular module.

    - **module_id** the id of the module \n
    Used in the visual editor.
    """
    return Module()


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
    Enables/ disables a module.

    - **module_id** the id of the module
    - **enable** whether it should be enabled or not
    - **is_trigger** ??? \n
    Disabled modules can't be used in the visual editor.
    """
    return None  # type: ignore


@router.post("/workflows/checkGraph", status_code=status.HTTP_200_OK, summary="Checks if the given graph is correct")
async def checkGraph(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    graph: WorkflowGraph,
) -> CheckGraphResponse:
    """
    Checks if the given graph is correct.

    - **graph** the workflow graph to check \n
    This will check if the graph is acyclic, if any node has multiple output connections
    and if there are path warnings.
    """
    return CheckGraphResponse()


@router.post(
    "/workflows/toggleWorkflows", status_code=status.HTTP_200_OK, summary="Enable/ disable the workflow feature"
)
async def toggleWorkflows(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> StandardStatusResponse:
    """
    Enable/ disable the workflow feature.

    Globally enables/ disables the workflow feature in your MISP instance.
    """
    return None  # type: ignore
