"""
MCP Server implementation with FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from .tools import MCPTools
from ..index.indexer import MetadataStore


class SearchRequest(BaseModel):
    query: str
    source_id: Optional[str] = None
    max_results: int = 50


class SchemaRequest(BaseModel):
    source_id: str
    table_name: str


class IndexRequest(BaseModel):
    source_id: str


class MCPServer:
    """MCP Server for Data Discovery Tool."""
    
    def __init__(self, metadata_store: MetadataStore):
        self.store = metadata_store
        self.tools = MCPTools(metadata_store)
        self.app = FastAPI(
            title="Data Discovery Tool MCP Server",
            description="MCP server for data discovery across multiple sources",
            version="1.0.0"
        )
        self._setup_routes()
        self._setup_cors()
    
    def _setup_cors(self):
        """Configure CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "Data Discovery Tool",
                "version": "1.0.0",
                "endpoints": [
                    "/list_sources",
                    "/search",
                    "/schema",
                    "/preview",
                    "/stats",
                    "/index_source"
                ]
            }
        
        @self.app.get("/list_sources")
        async def list_sources():
            return await self.tools.list_sources()
        
        @self.app.post("/search")
        async def search(request: SearchRequest):
            return await self.tools.search(
                request.query,
                request.source_id,
                request.max_results
            )
        
        @self.app.post("/schema")
        async def get_schema(request: SchemaRequest):
            return await self.tools.get_schema(
                request.source_id,
                request.table_name
            )
        
        @self.app.post("/preview")
        async def get_preview(request: SchemaRequest, limit: int = 10):
            return await self.tools.get_table_preview(
                request.source_id,
                request.table_name,
                limit
            )
        
        @self.app.get("/stats")
        async def get_stats():
            return await self.tools.get_source_stats()
        
        @self.app.post("/index_source")
        async def index_source(request: IndexRequest):
            return await self.tools.index_source(request.source_id)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server."""
        uvicorn.run(self.app, host=host, port=port)