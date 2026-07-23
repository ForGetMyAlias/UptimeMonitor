import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.checks.service import CheckerService
from src.domains.monitors.models import TargetSite


async def run_checks_job(session_factory: async_sessionmaker) -> None:
    async with session_factory() as session:
        stmt = select(TargetSite)
        result = await session.execute(stmt)
        sites = result.scalars().all()

        if not sites:
            return

        tasks = [CheckerService.ping_site(site, session) for site in sites]
        await asyncio.gather(*tasks, return_exceptions=True)


def create_scheduler(session_factory: async_sessionmaker) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    
    #Запуск проверок каждые 60с
    scheduler.add_job(
        run_checks_job,
        trigger="interval",
        seconds=60,
        args=[session_factory],
        id="ping_all_sites",
        replace_existing=True,
    )
    return scheduler