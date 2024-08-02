from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Tuple

from starlette import status

from mmisp.db.database import Session, get_db
from mmisp.lib.logging import ApplicationLogger
from mmisp.workflows.execution import VerbatimWorkflowInput, create_virtual_root_user, workflow_by_trigger_id
from mmisp.workflows.execution import execute_workflow as do_execute

from .error import LegacyMISPCompatibleHTTPException


@asynccontextmanager
async def application_logger() -> AsyncGenerator[ApplicationLogger, None]:
    """
    Creates an application logger instance and creates a new
    database session for it. The reason for that is that the "main"
    session's pending transaction will be rolled back if the workflow
    fails, all log messages would be lost, too.

    Since SQLAlchemy implements the UnitOfWork pattern internally,
    having no way of splitting changesets is by design.

    This speaks the (async) context-manager protocol. The transaction will
    be committed as soon as the scope of the `async with` statement
    is left.
    """
    session = await anext(get_db())
    yield ApplicationLogger(session)
    await session.commit()


async def execute_blocking_workflow(wf_name: str, db: Session, input: VerbatimWorkflowInput) -> None:
    """
    Executes a blocking workflow.

    After the workflow got executed, an HTTP error 400 will be returned
    if the workflow broke. The exception will be transformed into the format
    `{"message":"error message summary"}` to be compatible with the API from
    legacy MISP.

    Arguments:
        wf_name:    ID of the workflow trigger.
        db:         Main DB session. This one can have a pending transaction to
            edit models. Any pending changes will be rolled back on error.
        input:      Workflow payload.
    """
    result = await execute_workflow(wf_name, db, input)
    if result:
        execution_result, messages = result
        if not execution_result:
            messages_str = "\n".join(messages)
            raise LegacyMISPCompatibleHTTPException(
                status=status.HTTP_400_BAD_REQUEST,
                message=f"Workflow '{wf_name}' is blocking and failed with the following errors:\n{messages_str}",
            )


async def execute_workflow(wf_name: str, db: Session, input: VerbatimWorkflowInput) -> Tuple[bool, List[str]] | None:
    """
    Executes a workflow and returns the user messages and the execution result.

    Arguments:
        wf_name:    ID of the workflow trigger.
        db:         Main DB session. This one can have a pending transaction to
            edit models. Any pending changes will be rolled back on error.
        input:      Workflow payload.
    """
    async with application_logger() as logger:
        virtual_user = await create_virtual_root_user(db)
        if wf := await workflow_by_trigger_id(wf_name, db):
            return await do_execute(wf, virtual_user, input, db, logger)
    return None
