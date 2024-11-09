from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from database import DatabaseProvider, get_database_provider
from database.models import MonitoringRun
from database.schemas import MonitoringRunCreate, MonitoringRunRead

router = APIRouter(prefix="/monitoring_runs")


@router.get("/")
async def read_monitoring_runs(
    database: Annotated[DatabaseProvider, Depends(get_database_provider)]
) -> list[MonitoringRunRead]:
    """Returns a list of all monitoring runs.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=MonitoringRun, read_schema=MonitoringRunRead)


@router.get("/{monitoring_run_id}")
async def read_monitoring_run(
    monitoring_run_id: int, database: Annotated[DatabaseProvider, Depends(get_database_provider)]
) -> MonitoringRunRead:
    """Returns a single monitoring run.

    Args:
        monitoring_run_id (int): The ID of the monitoring run.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the monitoring run is not found.

    """
    if monitoring_run := await database.get(
        model=MonitoringRun, read_schema=MonitoringRunRead, filters=[MonitoringRun.id == monitoring_run_id]
    ):
        return monitoring_run
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitoring run not found")


@router.post("/")
async def create_monitoring_run(
    monitoring_run: MonitoringRunCreate, database: Annotated[DatabaseProvider, Depends(get_database_provider)]
) -> MonitoringRunRead:
    """Creates a new monitoring run.

    Args:
        monitoring_run (MonitoringRunCreate): The monitoring run to create.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the monitoring is not found.

    Returns:
        MonitoringRunRead: The created monitoring run.

    """
    try:
        return await database.create(model=MonitoringRun, data=monitoring_run, read_schema=MonitoringRunRead)
    except IntegrityError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitoring not found")
