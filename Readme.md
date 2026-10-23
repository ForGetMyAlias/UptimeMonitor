# Uptime Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Litestar](https://img.shields.io/badge/Litestar-2.x-EDB632?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Dishka](https://img.shields.io/badge/DI-Dishka-8A2BE2?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)

<p align="center">
  Асинхронный REST API для мониторинга доступности сайтов и времени отклика на базе <b>Litestar 2.x</b>, <b>SQLAlchemy 2.0</b>, <b>APScheduler</b> и <b>Dishka</b>.
</p>

[Особенности](#ключевые-особенности) •
[Стек](#стек-технологий) •
[Быстрый старт](#быстрый-старт) •
[API Reference](#api-reference)

---

</div>

## Ключевые особенности

- **Асинхронный стек**: от HTTP до базы данных всё на `async`/`await`: `Litestar`, `SQLAlchemy 2.0 (asyncio)`, драйвер `asyncpg`, проверки сайтов через `httpx`.
- **Отдельный воркер**: проверки вынесены из API в самостоятельный процесс на `APScheduler`, который каждую минуту опрашивает добавленные сайты. API и фоновая работа масштабируются и перезапускаются независимо.
- **Метрики за 24 часа**: аптайм в процентах, средний отклик в миллисекундах и число проверок считаются агрегирующим запросом на стороне базы.
- **Внедрение зависимостей**: сессии базы и сервисы собираются контейнером `Dishka` с областями `APP` и `REQUEST`, один и тот же провайдер используют и API, и воркер.
- **Доменная структура**: код разделён по доменам `monitors` и `checks`, внутри каждого свои модели, схемы и сервисы.
- **Валидация на входе**: адрес сайта проверяется как `HttpUrl`, интервал ограничен диапазоном от 10 до 3600 секунд.

---

## Стек технологий

| Компонент | Технология | Назначение |
| :--- | :--- | :--- |
| **Framework** | [Litestar](https://litestar.dev/) | ASGI веб-фреймворк, Swagger из коробки |
| **ORM** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (asyncio) | Асинхронная работа с базой, декларативные модели |
| **Database** | PostgreSQL 16 (`asyncpg`) | Хранение сайтов и результатов проверок |
| **Scheduler** | [APScheduler](https://apscheduler.readthedocs.io/) | Периодический запуск проверок в воркере |
| **HTTP Client** | [httpx](https://www.python-httpx.org/) | Асинхронные запросы к сайтам, таймаут 10 секунд |
| **DI** | [Dishka](https://dishka.readthedocs.io/) | Контейнер зависимостей для API и воркера |
| **Settings** | `pydantic-settings` | Конфигурация через переменные окружения и `.env` |
| **Package manager** | [uv](https://docs.astral.sh/uv/) | Быстрая установка зависимостей |

---

## Структура проекта

```tree
UptimeMonitor/
├── src/
│   ├── app.py                    # Litestar приложение, плагин SQLAlchemy, Dishka
│   ├── worker.py                 # Отдельный процесс: APScheduler и запуск проверок
│   ├── config.py                 # Настройки окружения (pydantic-settings)
│   ├── core/
│   │   ├── database.py           # SQLAlchemyAsyncConfig
│   │   ├── ioc.py                # Провайдер Dishka: engine, sessionmaker, сервисы
│   │   └── scheduler.py          # Планировщик внутри процесса API (воркером не используется)
│   └── domains/
│       ├── monitors/             # Домен сайтов
│       │   ├── controllers.py    # Роуты /api/v1/monitors
│       │   ├── models.py         # Base и модель TargetSite
│       │   ├── schemas.py        # DTO создания и ответа
│       │   └── service.py        # Бизнес-логика и расчёт метрик
│       └── checks/               # Домен проверок
│           ├── models.py         # Модель CheckResult
│           ├── schemas.py        # DTO результата проверки
│           └── service.py        # HTTP-проверка сайта через httpx
├── Dockerfile                    # Образ на python:3.12-slim с uv
├── docker-compose.yml            # db, web, worker
├── pyproject.toml                # Метаданные и зависимости
├── .env.example                  # Шаблон переменных окружения
└── Readme.md
```

---

## Быстрый старт

### 1. Docker Compose

Поднимает три контейнера: `db` (PostgreSQL), `web` (API) и `worker` (фоновые проверки).

```bash
git clone https://github.com/ForGetMyAlias/UptimeMonitor
cd UptimeMonitor
docker compose up --build -d
```

API доступно на `http://localhost:8000`.

### 2. Локальный запуск

```bash
# Установка зависимостей
uv sync

# Шаблон окружения
cp .env.example .env

# API
uv run uvicorn src.app:app --reload

# Воркер (в отдельном терминале)
uv run python -m src.worker
```

Для локального запуска нужен запущенный PostgreSQL, адрес которого указан в `DATABASE_URL`.

### 3. Конфигурация

Параметры [.env](.env.example):

```ini
PROJECT_NAME="Uptime Monitor"
DATABASE_URL="postgresql+asyncpg://uptime_user:uptime_password@localhost:5432/uptime_db"
```

| Переменная | По умолчанию | Описание |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `Uptime Monitor` | Название проекта |
| `DATABASE_URL` | `postgresql+asyncpg://uptime_user:uptime_password@localhost:5432/uptime_db` | Строка подключения к PostgreSQL |

Интерактивная документация:
- **Swagger UI**: [http://localhost:8000/schema/swagger](http://localhost:8000/schema/swagger)
- **Redoc**: [http://localhost:8000/schema/redoc](http://localhost:8000/schema/redoc)

---

## API Reference

### 1. Добавление сайта

```http
POST /api/v1/monitors
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "name": "Google",
  "url": "https://google.com",
  "interval_seconds": 60
}
```

| Поле | Обязательно | Описание |
| :--- | :--- | :--- |
| `name` | да | Название, от 1 до 100 символов |
| `url` | да | Адрес сайта, корректный `http(s)` URL |
| `interval_seconds` | нет | Интервал в секундах, от 10 до 3600, по умолчанию 60 |

**Ответ (`201 Created`):**
```json
{
  "id": "c6237b60-ef09-4bf9-897b-c3971e46955a",
  "name": "Google",
  "url": "https://google.com/",
  "interval_seconds": 60,
  "is_active": true
}
```

---

### 2. Список сайтов

```http
GET /api/v1/monitors
```

**Ответ (`200 OK`):**
```json
[
  {
    "id": "c6237b60-ef09-4bf9-897b-c3971e46955a",
    "name": "Google",
    "url": "https://google.com/",
    "interval_seconds": 60,
    "is_active": true
  }
]
```

---

### 3. Метрики за 24 часа

```http
GET /api/v1/monitors/{site_id}/stats
```

**Ответ (`200 OK`):**
```json
{
  "site_id": "c6237b60-ef09-4bf9-897b-c3971e46955a",
  "period_hours": 24,
  "total_checks": 1440,
  "uptime_persentage": 99.86,
  "avg_response_time_ms": 142.37
}
```

Если проверок за период не было, аптайм считается равным `100.0`, а средний отклик `0.0`.

---

### 4. Удаление сайта

```http
DELETE /api/v1/monitors/{site_id}
```

**Ответ:** `204 No Content`. Вместе с сайтом удаляются все его результаты проверок.
