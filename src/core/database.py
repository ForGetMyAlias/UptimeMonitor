from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig
from src.config import settings

db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DATABASE_URL,
    create_all=True,
)