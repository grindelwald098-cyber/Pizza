# Pizza

Backend API пиццерии (FastAPI).

Основная ветка: `backend-dev` (изменения только через pull request).

Frontend вынесен в отдельный репозиторий: [NextPizza](https://github.com/grindelwald098-cyber/NextPizza)  
Локально фронт лежит в `e:/my-projects/pizza-frontend`.

## Структура

```text
backend/     # FastAPI приложение, alembic, скрипты
docs/        # документация по домену и разборам
```

## Запуск backend

```bash
cd backend
docker compose up -d          # Postgres + S3 (LocalStack)
# скопируй backend/.env.example → backend/.env при необходимости
uvicorn app.main:app --reload
```

- API: http://localhost:8000/docs  
- S3 API: http://localhost:4566  
- Bucket: `pizza-media` (публичное чтение объектов)

Загрузка файла: `POST /media/upload` (multipart: `file`, опционально `folder`).  
Ответ содержит `url` — его можно сохранить в `image_url` товара/категории.

> Официальные Docker-образы MinIO сейчас недоступны без лицензии, поэтому локально
> поднят S3-совместимый LocalStack. Код использует `minio` SDK — позже можно
> переключить endpoint на настоящий MinIO / R2 / Yandex Object Storage без смены API.

См. также `docs/rukovodstvo.md`.
