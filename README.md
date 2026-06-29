# Тестовое задание: Fullstack-разработчик FastAPI + React

Fullstack-приложение для учёта внутренних заявок.

## Стек

### Backend

* Python 3.12
* FastAPI
* SQLAlchemy 2.x
* SQLite
* Pydantic Settings
* JWT-auth для админа
* In-memory rate limiting middleware
* Pytest

### Frontend

* React
* TypeScript
* Vite
* Fetch API
* CSS

### Infrastructure

* Docker
* Docker Compose
* Nginx для production-сборки frontend

## Возможности

* Создание заявки.
* Просмотр списка заявок.
* Backend-фильтрация по статусу и приоритету.
* Backend-поиск по `title` и `description`.
* Backend-сортировка по дате создания и приоритету.
* Backend-пагинация списка.
* Изменение статуса заявки.
* Удаление заявки только админом.
* Вход в админ-аккаунт.
* Состояния загрузки, пустого списка, успешных действий и ошибок API.
* Swagger/OpenAPI examples для основных схем и ошибок.
* Автотесты backend-бизнес-логики.

## Бизнес-правила

В системе есть дефолтный админ:

```
login: admin
password: admin
```

Админ нужен только для удаления заявок.

Правила статуса `done`:

* заявку в статусе `done` нельзя редактировать;
* заявку в статусе `done` нельзя удалить даже админу;
* заявку нельзя перевести из `done` обратно в другой статус;
* при нарушении бизнес-правил API возвращает осмысленный HTTP-ответ и понятное сообщение об ошибке.

## Модель заявки

| Поле          | Описание                                |
| ------------- | --------------------------------------- |
| `id`          | Уникальный идентификатор                |
| `title`       | Обязательное поле, от 3 до 120 символов |
| `description` | Необязательное поле, до 1000 символов   |
| `status`      | `new`, `in_progress`, `done`            |
| `priority`    | `low`, `normal`, `high`                 |
| `created_at`  | Дата и время создания в UTC             |
| `updated_at`  | Дата и время последнего изменения в UTC |

## Быстрый запуск через Docker Compose

Требуется запущенный Docker Desktop.

```
docker compose build
docker compose up
```

После запуска:

* Frontend: http://localhost:8080
* Backend healthcheck: http://127.0.0.1:8000/health
* Swagger/OpenAPI: http://127.0.0.1:8000/docs

Остановить контейнеры:

```
docker compose down
```

Остановить контейнеры и удалить volume с SQLite-базой:

```
docker compose down -v
```

## Локальный запуск без Docker

### Backend

Из корня проекта создать виртуальное окружение:

```
python -m venv .venv
```

Активировать окружение в Windows PowerShell:

```
.venv\Scripts\Activate.ps1
```

Установить зависимости:

```
pip install -r backend/requirements.txt
```

Запустить backend:

```
python -m uvicorn backend.app.main:app --reload
```

Backend будет доступен:

* http://127.0.0.1:8000
* http://127.0.0.1:8000/docs

### Frontend

В другом терминале:

```
cd frontend
npm install
npm run dev
```

Frontend будет доступен:

* http://localhost:5173

## Переменные окружения

Пример backend-переменных находится в `.env.example`.

Пример frontend-переменных находится в `frontend/.env.example`.

Для локального frontend-запуска:

```
cd frontend
Copy-Item .env.example .env -Force
```

## Backend API

Основные endpoints:

| Метод    | Endpoint                             | Описание                                                       |
| -------- | ------------------------------------ | -------------------------------------------------------------- |
| `GET`    | `/health`                            | Healthcheck                                                    |
| `POST`   | `/api/v1/auth/login`                 | Вход админа                                                    |
| `GET`    | `/api/v1/auth/me`                    | Текущий админ                                                  |
| `POST`   | `/api/v1/tickets`                    | Создание заявки                                                |
| `GET`    | `/api/v1/tickets`                    | Список заявок с фильтрацией, поиском, сортировкой и пагинацией |
| `PATCH`  | `/api/v1/tickets/{ticket_id}/status` | Частичное изменение статуса заявки                             |
| `DELETE` | `/api/v1/tickets/{ticket_id}`        | Удаление заявки админом                                        |

## Примеры запросов

### Создание заявки

```
curl -X POST http://127.0.0.1:8000/api/v1/tickets ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Printer is not working\",\"description\":\"Printer does not print\",\"priority\":\"high\"}"
```

### Получение списка

```
curl "http://127.0.0.1:8000/api/v1/tickets?search=printer&priority=high&sort_by=priority&sort_order=desc&page=1&page_size=10"
```

### Логин админа

```
curl -X POST http://127.0.0.1:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin\"}"
```

## Тесты

Backend-тесты:

```
python -m pytest backend/tests -q
```

Покрыты:

* авторизация админа;
* JWT;
* password hashing;
* создание заявки;
* валидация заявки;
* backend-поиск;
* backend-фильтрация;
* backend-сортировка;
* backend-пагинация;
* unicode-поиск;
* изменение статуса;
* запрет редактирования `done`;
* удаление только админом;
* запрет удаления `done`;
* rate limiting middleware.

## Проверка frontend-сборки

```
cd frontend
npm run build
```

## Docker-проверка

Проверить итоговую docker compose конфигурацию:

```
docker compose config
```

Собрать образы:

```
docker compose build
```

Запустить приложение:

```
docker compose up
```

## Rate limiting

Для API подключён in-memory rate limiter.

Значение по умолчанию:

```
100/minute
```

Настраивается переменной:

```
RATE_LIMIT_DEFAULT
```

Rate limiting применяется к маршрутам `/api/v1/*`.

## Архитектурные решения

* Поиск, фильтрация, сортировка и пагинация выполняются на backend.
* `PATCH /tickets/{id}/status` используется только для частичного изменения статуса, а не для полной замены заявки.
* Заявки в статусе `done` защищены и на frontend, и на backend.
* Удаление требует JWT-токен админа.
* SQLite используется согласно требованиям тестового задания.
* Docker Compose поднимает backend, frontend и volume для хранения SQLite-базы.
* Swagger/OpenAPI содержит examples для запросов, ответов и ошибок.
* Для тестового задания оставлены дефолтные креды `admin:admin`, потому что это прямо требуется условием.
