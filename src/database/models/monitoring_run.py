from datetime import datetime, timedelta

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Interval, String, text
from sqlalchemy.orm import Mapped, mapped_column

from database.enums import MonitoringRunStatus
from database.models.base import DatabaseModel


class MonitoringRun(DatabaseModel):
    """Monitoring run model."""

    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    monitoring_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey("monitorings.id"), index=True)
    log_file: Mapped[str | None] = mapped_column(String(200), nullable=True)
    duration: Mapped[timedelta | None] = mapped_column(Interval(), index=True, nullable=True)
    status: Mapped[MonitoringRunStatus] = mapped_column(
        Enum(*MonitoringRunStatus.values(), name="monitoring_run_status"),
        index=True,
        server_default=text(f"'{MonitoringRunStatus.SCHEDULED}'"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))
