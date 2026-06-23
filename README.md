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
