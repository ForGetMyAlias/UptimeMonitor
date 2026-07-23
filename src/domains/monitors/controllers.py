from typing import Any
from uuid import UUID
from litestar import Controller, delete, get, post
from dishka.integrations.litestar import FromDishka, inject

from src.domains.monitors.schemas import (
    CreateMonitorDTO,
    MonitorResponseDTO,
)
from src.domains.monitors.service import MonitorService


class MonitorController(Controller):
    path = "/api/v1/monitors"

    @get("/{site_id:uuid}/stats")
    @inject
    async def get_stats(
        self,
        site_id: UUID,
        service: FromDishka[MonitorService],
    ) -> dict[str, Any]:
        return await service.get_site_metrics(site_id)

    @post("/")
    @inject
    async def create_monitor(
        self,
        data: CreateMonitorDTO,
        service: FromDishka[MonitorService],
    ) -> MonitorResponseDTO:
        site = await service.create_site(data)
        return MonitorResponseDTO.model_validate(site)

    @get("/")
    @inject
    async def list_monitors(
        self,
        service: FromDishka[MonitorService],
    ) -> list[MonitorResponseDTO]:
        sites = await service.get_all_sites()
        return [MonitorResponseDTO.model_validate(site) for site in sites]

    @delete("/{site_id:uuid}")
    @inject
    async def delete_monitor(
        self,
        site_id: UUID,
        service: FromDishka[MonitorService],
    ) -> None:
        await service.delete_site(site_id)