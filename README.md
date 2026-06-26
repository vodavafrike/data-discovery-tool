# Data Discovery Tool

> Интеллектуальный инструмент для поиска данных в различных источниках с MCP-интерфейсом для AI-агентов

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Data Discovery Tool** — это сервис, который позволяет быстро находить данные в разных источниках (SQLite, CSV) по ключевым словам. Сервис индексирует структуру данных и предоставляет удобный поиск через **три интерфейса**:

- **CLI** — командная строка
- **Web UI** — веб-интерфейс на Streamlit
- **MCP Server** — REST API для AI-агентов

## Установка и запуск

### 1. Склонируйте репозиторий:
```powershell```
git clone https://github.com/vodavafrike/data-discovery-tool.git

cd data-discovery-tool

### 2. Cоздайте виртуальное окружение:
python -m venv venv

### 3. Активируйте его:
.\venv\bin\activate или .\venv\Scripts\activate

### 4. Установите зависимости:
python -m pip install -r requirements.txt

### 5. Загрузите демонстрационные данные:
Данные загружаются автоматически при первом запуске!
При первом запуске в папке data/ появятся:
sample_data/customers.csv
sample_data/orders.csv
sample.db (SQLite)

### 6. Запустите сервис:
### Режим CLI (командная строка):
python main.py --mode cli
### Web UI (Streamlit):
streamlit run web_app.py
### MCP Server (API для AI-агентов):
python server.py


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
