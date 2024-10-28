from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from database import DatabaseProvider
from database.models import Monitoring
from database.schemas import MonitoringCreate, MonitoringRead, MonitoringUpdate

router = APIRouter(prefix="/monitorings")


@router.get("/")
async def read_monitorings(database: Annotated[DatabaseProvider, Depends()]) -> list[MonitoringRead]:
    """Returns all monitorings.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=Monitoring, read_schema=MonitoringRead)


@router.get("/{monitoring_id}")
async def read_monitoring(monitoring_id: int, database: Annotated[DatabaseProvider, Depends()]) -> MonitoringRead:
    """Returns a monitoring by its ID.

    Args:
        monitoring_id (int): ID of the monitoring.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the monitoring is not found.

    """
    if monitoring := await database.get(
        model=Monitoring, read_schema=MonitoringRead, filters=[Monitoring.id == monitoring_id]
    ):
        return monitoring
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitoring not found")


@router.post("/")
async def create_monitoring(
    monitoring: MonitoringCreate, database: Annotated[DatabaseProvider, Depends()]
) -> MonitoringRead:
    """Creates a new monitoring.

    Args:
        monitoring (MonitoringCreate): Data to create the monitoring.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (400): If the monitoring already exists.
        HTTPException (404): If the user or marketplace is not found.

    Returns:
        MonitoringRead: Created monitoring.

    """
    try:
        return await database.create(model=Monitoring, data=monitoring, read_schema=MonitoringRead)
    except IntegrityError as error:
        error_str = str(error.orig)
        if "UniqueViolationError" in error_str:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Monitoring already exists")
        if "user_id" in error_str:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        if "marketplace_id" in error_str:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Marketplace not found")
        raise


@router.patch("/{monitoring_id}")
async def update_monitoring(
    monitoring_id: int,
    monitoring: MonitoringUpdate,
    database: Annotated[DatabaseProvider, Depends()],
) -> MonitoringRead:
    """Updates a monitoring by its ID.

    Args:
        monitoring_id (int): ID of the monitoring.
        monitoring (MonitoringUpdate): Data to update the monitoring.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the monitoring is not found.

    Returns:
        MonitoringRead: Updated monitoring.

    """
    try:
        return await database.update(
            model=Monitoring, data=monitoring, read_schema=MonitoringRead, filters=[Monitoring.id == monitoring_id]
        )
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitoring not found")


@router.delete("/{monitoring_id}")
async def delete_monitoring(monitoring_id: int, database: Annotated[DatabaseProvider, Depends()]) -> None:
    """Deletes a monitoring by its ID.

    Args:
        monitoring_id (int): ID of the monitoring.
        database (DatabaseProvider): Provider for the database.

    """
    await database.delete(model=Monitoring, filters=[Monitoring.id == monitoring_id])
