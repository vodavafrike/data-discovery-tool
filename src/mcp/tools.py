"""
MCP (Model Context Protocol) tools for AI agents.
"""
from typing import Dict, Any, List, Optional

from ..index.indexer import MetadataStore
from ..search.engine import SearchEngine


class MCPTools:
    """MCP tool implementations for data discovery."""
    
    def __init__(self, metadata_store: MetadataStore):
        self.store = metadata_store
        self.search_engine = SearchEngine(metadata_store)
    
    async def list_sources(self) -> Dict[str, Any]:
        """List all available data sources."""
        sources = self.store.get_sources()
        return {
            'status': 'success',
            'count': len(sources),
            'sources': sources
        }
    
    async def index_source(self, source_id: str) -> Dict[str, Any]:
        """Index a data source (or re-index if already indexed)."""
        if source_id in self.store.sources:
            return {
                'status': 'already_indexed',
                'message': f'Source {source_id} is already indexed',
                'source': self.store.sources[source_id].name
            }
        else:
            return {
                'status': 'error',
                'message': f'Source {source_id} not found'
            }
    
    async def search(self, query: str, source_id: Optional[str] = None, 
                     max_results: int = 50) -> Dict[str, Any]:
        """Search for tables and columns across indexed data sources."""
        results = self.search_engine.search(query, source_id, max_results)
        
        return {
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results)
        }
    
    async def get_schema(self, source_id: str, table_name: str) -> Dict[str, Any]:
        """Get detailed schema for a specific table."""
        schema = self.store.get_table_schema(source_id, table_name)
        
        if not schema:
            return {
                'status': 'error',
                'message': f'Table {table_name} not found in source {source_id}'
            }
        
        return {
            'status': 'success',
            'source_id': source_id,
            'table': table_name,
            'schema': {
                'name': schema.name,
                'columns': [
                    {
                        'name': col.name,
                        'type': col.data_type,
                        'nullable': col.nullable,
                        'sample_values': col.sample_values,
                        'is_primary_key': col.is_primary_key
                    }
                    for col in schema.columns
                ],
                'row_count': schema.row_count
            }
        }
    
    async def get_table_preview(self, source_id: str, table_name: str, 
                               limit: int = 10) -> Dict[str, Any]:
        """Get preview data from a table."""
        schema = self.store.get_table_schema(source_id, table_name)
        
        if not schema:
            return {
                'status': 'error',
                'message': f'Table {table_name} not found'
            }
        
        sample_rows = []
        for i in range(min(limit, 5)):
            row = {}
            for col in schema.columns:
                if col.sample_values and len(col.sample_values) > i:
                    row[col.name] = col.sample_values[i]
                else:
                    row[col.name] = None
            sample_rows.append(row)
        
        return {
            'status': 'success',
            'source_id': source_id,
            'table': table_name,
            'columns': [col.name for col in schema.columns],
            'sample_rows': sample_rows
        }
    
    async def get_source_stats(self) -> Dict[str, Any]:
        """Get statistics about all indexed sources."""
        sources = self.store.sources
        
        total_tables = 0
        total_columns = 0
        total_rows = 0
        
        for source in sources.values():
            total_tables += len(source.tables)
            for table in source.tables:
                total_columns += len(table.columns)
                total_rows += table.row_count or 0
        
        return {
            'status': 'success',
            'sources_count': len(sources),
            'total_tables': total_tables,
            'total_columns': total_columns,
            'total_rows': total_rows,
            'sources': [
                {
                    'id': sid,
                    'name': source.name,
                    'type': source.source_type,
                    'tables': len(source.tables)
                }
                for sid, source in sources.items()
            ]
        }