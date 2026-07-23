import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import make_async_container

from src.core.ioc import AppProvider
from src.domains.checks.service import CheckerService

async def run_checks_job(container):
    async with container() as request_container:
        cheker_service = await request_container.get(CheckerService)
        await cheker_service.check_all_active_sites()

async def main():
    container = make_async_container(AppProvider())
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(run_checks_job, 'interval', minutes=1, args=[container])
    scheduler.start()
    
    print("Фоновый процесс успешно запущен...")
    try:
        await asyncio.Event().wait()
    finally:
        await container.close()

if __name__ == "__main__":
    asyncio.run(main())