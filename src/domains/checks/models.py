from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domains.monitors.models import Base

if TYPE_CHECKING:
    from src.domains.monitors.models import TargetSite


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    site_id: Mapped[UUID] = mapped_column(ForeignKey("target_sites.id", ondelete="CASCADE"), index=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    site: Mapped["TargetSite"] = relationship(back_populates="checks")