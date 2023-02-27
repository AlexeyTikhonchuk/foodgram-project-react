|//![workflow](https://github.com/AlexeyTikhonchuk/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание проекта
Сервис позволяет пользователям публиковать рецепты,
подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов,
необходимых для приготовления одного или нескольких выбранных блюд.

Адрес ресурса: http://158.160.15.197/

## Запуск проекта на локальной машине:
Клонировать репозиторий:
`https://github.com/alexeytikhonchuk/foodgram-project-react.git`
В директории infra файл .env заполнить своими данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```
Создать и запустить контейнеры Docker, выполнить команду в терминале из папки infra:
`docker compose up -d`
После успешной сборки выполнить миграции:
`docker compose exec backend python manage.py migrate`
Создать суперпользователя:
`docker compose exec backend python manage.py createsuperuser`
Собрать статику:
`docker compose exec backend python manage.py collectstatic --noinput`
Наполнить базу данных содержимым из файла ingredients.json:
`docker compose exec backend python manage.py loaddata ingredients.json`

После запуска проект будут доступен по адресу: http://localhost/

Документация будет доступна по адресу: http://localhost/api/docs/

## Технологии: 
- Python
- Django
- Django REST Framework
- PostgreSQL
- NGINX
- gunicorn
- Docker
- GitHub Actions
- Yandex.Cloud

## Автор:
Алексей Тихончук
