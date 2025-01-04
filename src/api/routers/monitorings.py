from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import DatabaseProvider, get_database_dep
from database.enums import MonitoringRunStatus
from database.models import Advert, Marketplace, Monitoring, MonitoringRun
from database.schemas import (
    MonitoringCreate,
    MonitoringDetailsRead,
    MonitoringRead,
    MonitoringUpdate,
)

router = APIRouter(prefix="/monitorings")


@router.get("/")
async def read_monitorings(
    database: Annotated[DatabaseProvider, Depends(get_database_dep)], user_id: int | None = None
) -> list[MonitoringRead]:
    """Returns all monitorings.

    Args:
        database (DatabaseProvider): Provider for the database.
        user_id (int | None): ID of the user to filter the monitorings. Default is None.

    """
    filters = [Monitoring.user_id == user_id] if user_id is not None else None
    return await database.get_all(
        model=Monitoring,
        filters=filters,  # type: ignore[arg-type]
        order_by=[Monitoring.name.asc()],
        read_schema=MonitoringRead,
    )


@router.get("/{monitoring_id}")
async def read_monitoring(
    monitoring_id: int, database: Annotated[DatabaseProvider, Depends(get_database_dep)]
) -> MonitoringRead:
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


@router.get("/{monitoring_id}/details")
async def read_monitoring_details(
    monitoring_id: int, database: Annotated[DatabaseProvider, Depends(get_database_dep)]
) -> MonitoringDetailsRead:
    """Returns the details of a monitoring by its ID.

    Args:
        monitoring_id (int): ID of the monitoring.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the monitoring is not found.

    """
    query = (
        select(
            Monitoring.id,
            Monitoring.user_id,
            Monitoring.marketplace_id,
            Monitoring.name,
            Monitoring.url,
            Monitoring.run_interval,
            Monitoring.enabled,
            Monitoring.created_at,
            Monitoring.updated_at,
            Marketplace.name.label("marketplace_name"),
            select(MonitoringRun.created_at)
            .where(MonitoringRun.monitoring_id == monitoring_id, MonitoringRun.status == MonitoringRunStatus.SUCCESS)
            .order_by(MonitoringRun.created_at.desc())
            .limit(1)
            .label("last_successful_run"),
        )
        .where(Monitoring.id == monitoring_id)
        .join(Marketplace, Marketplace.id == Monitoring.marketplace_id)
    )

    if monitoring_details := await database.get_by_query(
        query=query, by_mappings=True, read_schema=MonitoringDetailsRead
    ):
        return monitoring_details
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitoring not found")


@router.post("/")
async def create_monitoring(
    monitoring: MonitoringCreate, database: Annotated[DatabaseProvider, Depends(get_database_dep)]
) -> MonitoringRead:
    """Creates a new monitoring.

    Args:
        monitoring (MonitoringCreate): Data to create the monitoring.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (409): If the monitoring already exists.
        HTTPException (404): If the user or marketplace is not found.

    Returns:
        MonitoringRead: Created monitoring.

    """
    try:
        return await database.create(model=Monitoring, data=monitoring, read_schema=MonitoringRead)
    except IntegrityError as error:
        error_str = str(error.orig)
        if "UniqueViolationError" in error_str:
            raise HTTPException(status.HTTP_409_CONFLICT, "Monitoring already exists")
        if "user_id" in error_str:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        if "marketplace_id" in error_str:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Marketplace not found")
        raise


@router.patch("/{monitoring_id}")
async def update_monitoring(
    monitoring_id: int,
    monitoring: MonitoringUpdate,
    database: Annotated[DatabaseProvider, Depends(get_database_dep)],
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
async def delete_monitoring(
    monitoring_id: int, database: Annotated[DatabaseProvider, Depends(get_database_dep)]
) -> dict[str, str]:
    """Deletes a monitoring by its ID.

    Args:
        monitoring_id (int): ID of the monitoring.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the monitoring is not found.

    Returns:
        dict[str, str]: The message that the monitoring was deleted.

    """
    try:
        await database.delete(model=Advert, filters=[Advert.monitoring_id == monitoring_id])
        await database.delete(model=MonitoringRun, filters=[MonitoringRun.monitoring_id == monitoring_id])
        await database.delete(model=Monitoring, filters=[Monitoring.id == monitoring_id])
        return {"detail": "Monitoring deleted successfully"}
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Monitoring not found")
