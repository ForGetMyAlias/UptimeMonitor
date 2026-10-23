import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import make_async_container

from src.core.ioc import AppProvider
from src.domains.checks.service import CheckerService


async def run_checks_job(container):
    async with container() as request_container:
        checker_service = await request_container.get(CheckerService)
        await checker_service.check_all_active_sites()


async def main():
    container = make_async_container(AppProvider())
    scheduler = AsyncIOScheduler()

    # Раз в 10 секунд смотрим каких сайтов подошёл interval_seconds (минимум у сайта 10 секунд).
    scheduler.add_job(run_checks_job, "interval", seconds=10, args=[container], max_instances=1, coalesce=True)
    scheduler.start()

    print("Фоновый процесс успешно запущен...")
    try:
        await asyncio.Event().wait()
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
