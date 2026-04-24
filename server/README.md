# Minecraft Coach Server

Серверная часть теперь выполняет три задачи сразу:

- отдаёт сайт из папки `Site/`
- отдаёт загрузку актуального desktop-приложения и модулей
- принимает и хранит удалённый снимок конкретной сессии для входа по `program_id + parent password`

## Что уже реализовано

- `GET /`
  Открывает сайт загрузки и мониторинга.
- `GET /downloads/catalog`
  Возвращает каталог актуального `.exe` и доступных модулей.
- `GET /downloads/app/latest`
  Отдаёт текущий `dist/MinecraftCoach.exe`.
- `GET /downloads/modules/{slug}.zip`
  Собирает ZIP модуля на лету из папки `modules/{slug}`.
- `POST /auth/login`
  Вход по `program_id + parent_password`.
- `GET /dashboard`
  Возвращает удалённый снимок сессии после логина.
- `POST /sync/push`
  Desktop-приложение отправляет на сервер текущий снимок состояния.

## Структура

- `app/main.py`
  Основной FastAPI backend.
- `app/storage.py`
  Простое файловое хранилище удалённых снимков и сессий.
- `postgresql_schema.sql`
  Заготовка будущей схемы для PostgreSQL.
- `api_contract.md`
  Черновой API-контракт.

## Где лежат данные

Текущее простое хранилище:

- `server/data/remote_state.json`

Там хранятся:

- удалённые снимки программ по `program_id`
- хеш пароля родителя
- время последнего обновления

Сессии входа в сайт живут в памяти процесса и сбрасываются при перезапуске backend.

## Как обновлять контент сайта

### Новая версия приложения

Просто замените:

- `dist/MinecraftCoach.exe`

### Новые модули

Просто добавьте или обновите папки в:

- `modules/`

Сайт и backend автоматически увидят изменения.

## Как запустить локально

Из корня проекта:

```bash
pip install -r server/requirements.txt
uvicorn server.app.main:app --host 0.0.0.0 --port 8000
```

После запуска:

- сайт: `http://localhost:8000`
- health-check: `http://localhost:8000/health`

## Как подключить desktop-приложение

1. Откройте в программе `Настройки`
2. Введите `Server API URL`
3. Сохраните настройки
4. Программа начнёт отправлять на сервер снимки текущей сессии

## Безопасность

- Сайт открывает мониторинг только после входа по `ID программы + пароль родителя`
- Сервер хранит только хеш пароля, а не сырой пароль
- Для публичного интернета используйте HTTPS
- Для production позже стоит заменить файловое хранилище на PostgreSQL и добавить rate limiting

## Базовая защита API

- Для `POST /sync/push` теперь обязателен заголовок `Idempotency-Key`
- На backend добавлены rate limiting и throttling по IP для логина, sync и download-маршрутов
- Сервер больше не принимает произвольные поля в JSON-моделях: лишние поля отклоняются
- `CORS` больше не открыт на `*` по умолчанию. Базовый allowlist:
  - `https://minecraftcoach.pl`
  - `https://www.minecraftcoach.pl`
  - `http://localhost:8000`
  - `http://127.0.0.1:8000`
- При необходимости список можно переопределить через переменную окружения:
  - `MINECRAFT_COACH_ALLOWED_ORIGINS`
  - пример: `https://minecraftcoach.pl,https://admin.minecraftcoach.pl`

## PostgreSQL backend

- Для production backend теперь умеет работать через PostgreSQL вместо `server/data/remote_state.json`
- В PostgreSQL хранятся:
  - remote snapshots
  - login sessions
  - audit log
  - idempotency keys
  - rate-limit hits
  - rate-limit violations
  - IP bans
- Быстрый запуск и переменные окружения описаны в:
  - `server/SETUP_BACKEND.txt`
  - `server/backend.env.example`
