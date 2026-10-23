from datetime import datetime, timedelta, timezone
from uuid import UUID
from litestar.exceptions import NotFoundException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.checks.models import CheckResult
from src.domains.monitors.models import TargetSite
from src.domains.monitors.schemas import CreateMonitorDTO


class MonitorService:
    def __init__(self, session: AsyncSession):
        self.session= session

    async def _get_or_404(self, site_id: UUID) -> TargetSite:
        site = await self.session.get(TargetSite, site_id)
        if site is None:
            raise NotFoundException(detail="Site not found")
        return site

    async def create_site(self, data: CreateMonitorDTO) -> TargetSite:
        site = TargetSite(name=data.name, url=str(data.url), interval_seconds=data.interval_seconds)
        self.session.add(site)
        await self.session.commit()
        return site

    async def get_all_sites(self) -> list[TargetSite]:
        result = await self.session.execute(select(TargetSite).order_by(TargetSite.created_at))
        return list(result.scalars().all())

    async def delete_site(self, site_id: UUID) -> None:
        await self._get_or_404(site_id)
        # Удаляем запросами, а не через ORM: каскад в async сессии пытается лениво грузить связи и падает.
        await self.session.execute(delete(CheckResult).where(CheckResult.site_id == site_id))
        await self.session.execute(delete(TargetSite).where(TargetSite.id == site_id))
        await self.session.commit()

    async def get_site_metrics(self, site_id: UUID, hours: int = 24) -> dict:
        # Считает аптайм и средний пинг за указаный период
        await self._get_or_404(site_id)
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Выборка всех проверок за период
        stmt = select(
            func.count(CheckResult.id).label("total"),
            func.count().filter(CheckResult.is_successful == True).label("successful"),
            func.avg(CheckResult.response_time_ms).label("avg_latency"),
        ).where(
            CheckResult.site_id == site_id,
            CheckResult.checked_at >= since,
        )

        res = (await self.session.execute(stmt)).one()

        total = res.total or 0
        successful = res.successful or 0
        avg_latency = round(res.avg_latency, 2) if res.avg_latency else 0.0

        uptime_percentage = round((successful / total * 100), 2) if total > 0 else 100.0
        
        return {
            "site_id": site_id,
            "period_hours": hours,
            "total_checks": total,
            "uptime_percentage": uptime_percentage,
            "avg_response_time_ms": avg_latency,
        }