from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import Litestar
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin

from src.core.database import db_config
from src.core.scheduler import create_scheduler
from src.domains.monitors.controllers import MonitorController

@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    session_factory = db_config.create_session_maker()

    scheduler = create_scheduler(session_factory)
    scheduler.start()

    yield

    scheduler.shutdown()


app = Litestar(
    route_handlers=[MonitorController],
    plugins=[SQLAlchemyPlugin(db_config)],
    lifespan=[lifespan],
)