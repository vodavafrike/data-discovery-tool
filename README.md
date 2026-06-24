# Data Discovery Tool

> Интеллектуальный инструмент для поиска данных в различных источниках с MCP-интерфейсом для AI-агентов

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## О проекте

**Data Discovery Tool** — это сервис, который позволяет быстро находить данные в разных источниках (SQLite, CSV) по ключевым словам. Сервис индексирует структуру данных и предоставляет удобный поиск через CLI или API

## Скриншоты

### Запуск проекта
![Запуск](screenshots/1_startup.png)

### Список источников данных
![Список источников](screenshots/2_list.png)

### Поиск по ключевому слову
![Поиск](screenshots/3_search.png)

### Схема таблицы
![Схема таблицы](screenshots/4_schema.png)

### Статистика
![Статистика](screenshots/5_stats.png)

### Особенности

- **Подключение к разным источникам**: SQLite, CSV файлы
- **Индексация метаданных**: таблицы, колонки, типы данных
- **Умный поиск**: с релевантностью и нечетким поиском
- **MCP-интерфейс**: для интеграции с AI-агентами
- **CLI и API**: удобный интерфейс для пользователей
- **Примеры данных**: автоматическая загрузка тестовых данных

### Архитектура
![Архитектура Data Discovery Tool](screenshots/architecture.png)

## Веб-интерфейс

### Главная страница
![Главная страница](screenshots/web_1_main.png)

### Результаты поиска
![Результаты поиска](screenshots/web_2_search.png)

### Схема таблицы
![Схема таблицы](screenshots/web_3_schema.png)

## MCP Server (API для AI-агентов)

MCP сервер предоставляет REST API для AI-агентов, позволяя им выполнять поиск данных программно.

### Документация API (Swagger UI)

![Swagger UI](screenshots/api_swagger.png)

### Список источников данных

Запрос: `GET /list_sources`

![Список источников](screenshots/api_list_sources.png)

### Поиск по ключевому слову

Запрос: `GET /search/{query}`

Пример: `GET /search/customer`

![Поиск](screenshots/api_search.png)

### Статистика

Запрос: `GET /stats`

![Статистика](screenshots/api_stats.png)

### Как это работает

AI-агент (нейросеть) может отправлять HTTP-запросы к MCP серверу:

```bash
# Получить список источников
curl http://localhost:8005/list_sources

# Поиск по ключевому слову
curl http://localhost:8005/search/customer

# Получить статистику
curl http://localhost:8005/stats