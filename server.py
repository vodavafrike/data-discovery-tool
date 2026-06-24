"""
Минимальный MCP сервер.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from src.index.indexer import MetadataStore
from src.search.engine import SearchEngine

# Создаём приложение
app = FastAPI(title="Data Discovery Tool", version="1.0.0")

# Загружаем данные
store = MetadataStore()
search_engine = SearchEngine(store)


@app.get("/")
async def root():
    return {"message": "Data Discovery Tool MCP Server", "sources": len(store.sources)}


@app.get("/list_sources")
async def list_sources():
    return {"sources": store.get_sources()}


@app.get("/search/{query}")
async def search(query: str):
    results = search_engine.search(query)
    return {"query": query, "count": len(results), "results": results}


@app.get("/stats")
async def stats():
    sources = store.get_sources()
    total_tables = sum(s.get('table_count', 0) for s in sources)
    return {
        "sources": len(sources),
        "tables": total_tables,
        "details": sources
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 MCP Server запущен на http://localhost:8005")
    print("📖 Документация: http://localhost:8005/docs")
    uvicorn.run(app, host="127.0.0.1", port=8005)