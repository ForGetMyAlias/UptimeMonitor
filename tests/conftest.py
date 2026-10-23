import os
import tempfile

# Настройки читаются при импорте, поэтому подставляем тестовую базу до любых импортов из src.
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mkdtemp()}/test.db"
