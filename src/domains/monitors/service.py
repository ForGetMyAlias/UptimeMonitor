from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.monitors.models import TargetSite
from src.domains.checks.models import CheckResult

class MonitorService:
    def __init__(self, session: AsyncSession):
        self.session= session

    async def get_site_metrics(self, site_id: UUID, hours: int = 24) -> dict:
        # Считает аптайм и средний пинг за указаный период
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
            "uptime_persentage": uptime_percentage,
            "avg_response_time_ms": avg_latency,
        }