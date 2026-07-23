from typing import AsyncIterable
from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings
from src.domains.monitors.service import MonitorService
from src.domains.checks.service import CheckerService

class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(settings.DATABASE_URL)
    
    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)
    
    @provide(scope=Scope.REQUEST)
    async def get_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session
    
    monitor_service = provide(MonitorService, scope=Scope.REQUEST)
    checker_service = provide(CheckerService, scope=Scope.REQUEST)