from datetime import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import BIGINT, ENUM, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from database.enums import RunStatus
from database.models.base import BaseModel


class MonitoringRun(BaseModel):
    """Monitoring run model."""

    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    monitoring_id: Mapped[int] = mapped_column(BIGINT(), ForeignKey("monitorings.id"))
    log_file: Mapped[str] = mapped_column(VARCHAR(100))
    status: Mapped[RunStatus] = mapped_column(
        ENUM(RunStatus), index=True, server_default=text(RunStatus.SCHEDULED.value)
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=text("now()"))
