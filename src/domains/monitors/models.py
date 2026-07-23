from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.domains.checks.models import CheckResult


class Base(DeclarativeBase):
    pass


class TargetSite(Base):
    __tablename__ = "target_sites"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500), index=True)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # <-- Добавляем эту строку
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    checks: Mapped[list["CheckResult"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )