# airflow-data-pipeline-lab
Лабораторная работа по теме AirFlow

# Лабораторная работа: Автоматизация сбора данных с помощью Apache Airflow

## Полезные команды

```bash
# Клонируем репозиторий
git clone <your-repo-url>
cd airflow-data-pipeline-lab
```
```bash
# Запуск
docker compose up -d

# Проверка, что всё работает
docker ps

# Остановить всё
docker compose down

# Посмотреть логи Airflow
docker compose logs airflow

# Перезапустить конкретный сервис
docker compose restart postgres-dwh

# Полная очистка (удалить все данные)
docker compose down -v

# Проверка текущих баз
docker exec -it postgres-dwh psql -U dwh_user -d dwh -c "\l"

# Проверка сервиса
docker logs airflow-lab --tail=30

# Создание базы airflow
docker compose restart airflow

# Рестарт сервиса airflow
docker compose restart airflow 
```

## Доступ к сервисам

| Сервис              | URL                     | Логин / Пароль                          |
|---------------------|-------------------------|-----------------------------------------|
| Airflow             | http://localhost:8080   | airflow / airflow                       |
| MinIO Console       | http://localhost:9001   | minioadmin / minioadmin                 |
| PostgreSQL (DWH)    | localhost:5433          | dwh_user / dwh_pass                     |

## Подключения к базам данных

| Назначение | Хост | Порт | База данных | Пользователь | Пароль |
|------------|------|------|-------------|--------------|--------|
| **Source DB** (источник) | `localhost` | `5434` | `source_db` | `source_user` | `source_pass` |
| **DWH** (хранилище) | `localhost` | `5433` | `dwh` | `dwh_user` | `dwh_pass` |
| **Airflow DB** (метабаза) | `localhost` | `5433` | `airflow` | `airflow` | `airflow` |

---

## Подключения к веб-сервисам

| Сервис | URL | Логин | Пароль |
|--------|-----|-------|--------|
| **Airflow** | `http://localhost:8080` | `airflow` | `airflow` |
| **MinIO Console** | `http://localhost:9001` | `minioadmin` | `minioadmin` |
| **Mock API** | `http://localhost:8000` | - | - |

---

## Порт

| Сервис | Порт |
|--------|------|
| Source DB (PostgreSQL) | `5434` |
| DWH (PostgreSQL) | `5433` |
| Airflow Web UI | `8080` |
| MinIO API | `9000` |
| MinIO Console | `9001` |
| Mock API | `8000` |

