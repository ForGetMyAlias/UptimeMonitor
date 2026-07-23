import time
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.monitors.models import TargetSite
from src.domains.checks.models import CheckResult
class CheckerService:
    @staticmethod
    async def ping_site(site: TargetSite, session: AsyncSession) -> CheckResult:
        #делает асинхронный http запрос к сайту и сохраняет результат в БД
        start_time = time.perf_counter()

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(site.url)
                duration_ms = (time.perf_counter() - start_time) * 1000
                is_ok = 200 <= response.status_code < 300
                result = CheckResult(
                    site_id=site.id,
                    start_code=response.status_code,
                    response_time_ms=round(duration_ms, 2),
                    is_successful=is_ok,
                )
            except httpx.RequestError as exc:
                duration_ms = (time.perf_counter() - start_time) * 1000
                result = CheckResult(
                    site_id=site.id,
                    status_code=None,
                    response_time_ms=round(duration_ms, 2),
                    id_successful=False,
                    error_message=str(exc),
                )

            session.add(result)
            await session.commit()
            return result