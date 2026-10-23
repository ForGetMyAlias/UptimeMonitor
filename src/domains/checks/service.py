import asyncio
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.checks.models import CheckResult
from src.domains.monitors.models import TargetSite


class CheckerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def probe(site: TargetSite) -> CheckResult:
        # Делает http запрос к сайту и возвращает результат, в базу сам ничего не пишет.
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(site.url)
            return CheckResult(
                site_id=site.id,
                status_code=response.status_code,
                response_time_ms=round((time.perf_counter() - start) * 1000, 2),
                is_successful=200 <= response.status_code < 300,
            )
        except httpx.HTTPError as exc:
            return CheckResult(
                site_id=site.id,
                status_code=None,
                response_time_ms=round((time.perf_counter() - start) * 1000, 2),
                is_successful=False,
                error_message=(str(exc) or type(exc).__name__)[:500],
            )

    @staticmethod
    async def ping_site(site: TargetSite, session: AsyncSession) -> CheckResult:
        # Проверяет один сайт и сохраняет результат в БД.
        result = await CheckerService.probe(site)
        session.add(result)
        await session.commit()
        return result

    async def check_all_active_sites(self) -> int:
        # Проверяет активные сайты, у которых подошёл interval_seconds. Возвращает сколько проверил.
        last = (
            select(CheckResult.site_id, func.max(CheckResult.checked_at).label("last_at"))
            .group_by(CheckResult.site_id)
            .subquery()
        )
        rows = (
            await self.session.execute(
                select(TargetSite, last.c.last_at)
                .outerjoin(last, last.c.site_id == TargetSite.id)
                .where(TargetSite.is_active.is_(True))
            )
        ).all()

        now = datetime.now(timezone.utc)
        due = []
        for site, last_at in rows:
            if last_at is not None and last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=timezone.utc)
            if last_at is None or (now - last_at).total_seconds() >= site.interval_seconds:
                due.append(site)
        if not due:
            return 0

        # Запросы идут параллельно, а в базу пишем одной сессией после них.
        results = await asyncio.gather(*(self.probe(site) for site in due))
        self.session.add_all(results)
        await self.session.commit()
        return len(results)
