"""
Factory for creating connector instances.
"""
from typing import Dict, Any
from .base import BaseConnector
from .sqlite_connector import SQLiteConnector
from .csv_connector import CSVConnector


class ConnectorFactory:
    """Factory class for creating data source connectors."""
    
    @staticmethod
    def create_connector(source_type: str, source_id: str, config: Dict[str, Any]) -> BaseConnector:
        """Create a connector instance based on source type."""
        if source_type == 'sqlite':
            return SQLiteConnector(source_id, config)
        elif source_type == 'csv':
            return CSVConnector(source_id, config)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")