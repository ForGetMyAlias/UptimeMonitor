# Uptime Monitor API 🌐

Асинхронное API на Litestar и SQLAlchemy 2.0 для отслеживания доступности сайтов и проверки пинга. 

Проект написан с разделением по доменам (DDD), использует полностью асинхронный стек и крутится в Docker.

---

## 🛠 Что внутри

* Litestar — в качестве ASGI-фреймворка (быстрый и с хорошей типизацией из коробки).
* SQLAlchemy 2.0 (AsyncIO) + PostgreSQL — работа с базой данных.
* APScheduler — крутит фоновый таск, который каждые N секунд параллельно пингует добавленные сайты через httpx.
* uv — быстрый менеджер зависимостей.
* Docker / Docker Compose — упаковано и ready-to-use.

---

## 🚀 Как запустить

### Быстрый старт через Docker Compose

1. Клонируй репозиторий:
   git clone https://github.com/ForGetMyAlias/UptimeMonitor
   cd UptimeMonitor

2. Подними контейнеры (PostgreSQL + App):
   docker compose up --build -d

Сервер поднимется на http://localhost:8000.

---

### Локальная разработка (через uv)

1. Установи зависимости:
   uv sync

2. Запусти Uvicorn:
   uv run uvicorn src.app:app --reload

---

## 📌 Документация API

После запуска открывай Swagger UI в браузере:
http://localhost:8000/schema/swagger

Основные эндпоинты:
* POST /api/v1/monitors — Добавить сайт в систему
* GET /api/v1/monitors — Посмотреть список сайтов
* GET /api/v1/monitors/{site_id}/stats — Получить Uptime (%) и средний отклик (ms) за 24 часа
