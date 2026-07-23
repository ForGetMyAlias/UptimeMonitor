from litestar import Litestar
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka

from src.core.database import db_config
from src.domains.monitors.controllers import MonitorController
from src.core.ioc import AppProvider

container = make_async_container(AppProvider())

app = Litestar(
    route_handlers=[MonitorController],
    plugins=[SQLAlchemyPlugin(db_config)],
)

setup_dishka(container, app)