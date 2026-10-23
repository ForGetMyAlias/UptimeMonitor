from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig

from src.config import settings
from src.domains.checks import models as _checks_models  # noqa: F401  (регистрирует таблицу check_results)
from src.domains.monitors.models import Base

db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DATABASE_URL,
    metadata=Base.metadata,
    create_all=True,
)
