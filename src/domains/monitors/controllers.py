from uuid import UUID
from litestar import Controller, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.monitors.models import TargetSite
from src.domains.monitors.schemas import CreateMonitorDTO, MonitorResponseDTO
from src.domains.monitors.service import MonitorService


class MonitorController(Controller):
    path = "/api/v1/monitors"

    @post("/")
    async def create_monitor(
        self, data: CreateMonitorDTO, db_session: AsyncSession
    ) -> MonitorResponseDTO:
        #Добавление нового сайта на мониторинг
        site = TargetSite(
            name=data.name, 
            url=str(data.url), 
            interval_seconds=data.interval_seconds
        )
        db_session.add(site)
        await db_session.commit()
        return site

    @get("/{site_id:uuid}/stats")
    async def get_monitor_stats(
        self, site_id: UUID, db_session: AsyncSession, hours: int = 24
    ) -> dict:
        #Получение статистики аптайма и пинга
        service = MonitorService(db_session)
        return await service.get_site_metrics(site_id=site_id, hours=hours)