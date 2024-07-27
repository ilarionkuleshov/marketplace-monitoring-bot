from datetime import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import BIGINT, ENUM, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from database.enums import RunStatus
from database.models.base import Base


class MonitoringRun(Base):
    """Monitoring run model."""

    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    monitoring_id: Mapped[int] = mapped_column(BIGINT(), ForeignKey("monitorings.id"))
    log_file: Mapped[str | None] = mapped_column(VARCHAR(100), nullable=True)
    status: Mapped[RunStatus] = mapped_column(
        ENUM(*RunStatus.values(), name="run_status"), index=True, server_default=text(f"'{RunStatus.SCHEDULED}'")
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=text("now()"))
