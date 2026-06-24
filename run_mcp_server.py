"""
Простой запуск MCP сервера.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.index.indexer import MetadataStore
from src.mcp.server import MCPServer
import uvicorn

print("📊 Загрузка данных...")
store = MetadataStore()

if store.sources:
    print(f"✅ Найдено {len(store.sources)} источников: {list(store.sources.keys())}")
else:
    print("⚠️ Нет данных! Запустите сначала python main.py --mode cli")
    sys.exit(1)

print("🚀 Запуск MCP сервера на порту 8000")
print("📖 Документация: http://localhost:8000/docs")
print("🔍 Проверка: http://localhost:8000/list_sources")
print("Нажмите CTRL+C для остановки")

server = MCPServer(store)
uvicorn.run(server.app, host="0.0.0.0", port=8001)