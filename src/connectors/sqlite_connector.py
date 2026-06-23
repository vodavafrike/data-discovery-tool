"""
SQLite connector implementation.
"""
from typing import Dict, List, Any
from datetime import datetime
import aiosqlite

from .base import BaseConnector, SourceMetadata, TableMetadata, ColumnMetadata


class SQLiteConnector(BaseConnector):
    """Connector for SQLite databases."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.connection = None
        self.db_path = config.get('db_path')
        
    async def connect(self) -> bool:
        """Establish connection to SQLite database."""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            await self.connection.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite: {e}")
    
    async def disconnect(self) -> bool:
        """Close SQLite connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
        return True
    
    async def get_metadata(self) -> SourceMetadata:
        """Extract comprehensive metadata from SQLite database."""
        if not self.connection:
            await self.connect()
        
        tables = []
        
        cursor = await self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        table_rows = await cursor.fetchall()
        
        for (table_name,) in table_rows:
            table_meta = await self.get_table_schema(table_name)
            tables.append(table_meta)
        
        return SourceMetadata(
            source_id=self.source_id,
            source_type='sqlite',
            name=self.config.get('name', 'SQLite Database'),
            description=self.config.get('description', ''),
            tables=tables,
            connection_info={'db_path': self.db_path},
            last_indexed=datetime.now()
        )
    
    async def get_table_schema(self, table_name: str) -> TableMetadata:
        """Get schema for a specific table."""
        if not self.connection:
            await self.connect()
        
        columns = []
        
        cursor = await self.connection.execute(f"PRAGMA table_info({table_name})")
        column_info = await cursor.fetchall()
        
        sample_data = await self.get_table_data(table_name, limit=3)
        
        for col in column_info:
            col_name = col[1]
            col_type = col[2]
            nullable = not bool(col[3])
            is_pk = bool(col[5])
            
            sample_values = [
                row.get(col_name) for row in sample_data 
                if row.get(col_name) is not None
            ][:3]
            
            columns.append(ColumnMetadata(
                name=col_name,
                data_type=col_type,
                nullable=nullable,
                sample_values=sample_values,
                is_primary_key=is_pk
            ))
        
        cursor = await self.connection.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_row = await cursor.fetchone()
        row_count = count_row[0] if count_row else 0
        
        return TableMetadata(
            name=table_name,
            columns=columns,
            row_count=row_count
        )
    
    async def get_table_data(self, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        if not self.connection:
            await self.connect()
        
        cursor = await self.connection.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = await cursor.fetchall()
        
        column_names = [description[0] for description in cursor.description]
        
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        
        return result