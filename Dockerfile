FROM python:3.12-slim

# Отключаем создание .pyc файлов и включаем unbuffered логгирование
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Ставим uv
RUN pip install --no-cache-dir uv

# Копируем описание зависимостей и устанавливаем их
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# Копируем весь исходный код проекта
COPY . .

EXPOSE 8000

# Запускаем Litestar приложение через uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]