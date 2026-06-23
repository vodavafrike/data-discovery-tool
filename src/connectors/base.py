"""
Base connector interface for data sources.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ColumnMetadata:
    """Metadata for a column/field in a data source."""
    name: str
    data_type: str
    nullable: bool = True
    description: Optional[str] = None
    sample_values: List[Any] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False


@dataclass
class TableMetadata:
    """Metadata for a table/collection in a data source."""
    name: str
    columns: List[ColumnMetadata]
    row_count: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SourceMetadata:
    """Metadata for a data source."""
    source_id: str
    source_type: str
    name: str
    description: str
    tables: List[TableMetadata]
    connection_info: Dict[str, Any]
    last_indexed: Optional[datetime] = None


class BaseConnector(ABC):
    """Abstract base class for all data source connectors."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        self.source_id = source_id
        self.config = config
        self.metadata = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to the data source."""
        pass
    
    @abstractmethod
    async def get_metadata(self) -> SourceMetadata:
        """Extract metadata from the data source."""
        pass
    
    @abstractmethod
    async def get_table_data(self, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        pass
    
    @abstractmethod
    async def get_table_schema(self, table_name: str) -> TableMetadata:
        """Get schema information for a specific table."""
        pass
    
    def get_source_id(self) -> str:
        """Return the source ID."""
        return self.source_id