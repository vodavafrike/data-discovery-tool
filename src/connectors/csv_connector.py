"""
CSV files connector implementation.
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from .base import BaseConnector, SourceMetadata, TableMetadata, ColumnMetadata


class CSVConnector(BaseConnector):
    """Connector for CSV files in a directory."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.data_dir = Path(config.get('data_dir', './data'))
        self.files = []
        
    async def connect(self) -> bool:
        """Scan directory for CSV files."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        self.files = list(self.data_dir.glob('*.csv'))
        return True
    
    async def disconnect(self) -> bool:
        """No-op for CSV connector."""
        return True
    
    async def get_metadata(self) -> SourceMetadata:
        """Extract metadata from CSV files."""
        if not self.files:
            await self.connect()
        
        tables = []
        
        for csv_file in self.files:
            table_name = csv_file.stem
            table_meta = await self.get_table_schema(table_name)
            tables.append(table_meta)
        
        return SourceMetadata(
            source_id=self.source_id,
            source_type='csv',
            name=self.config.get('name', 'CSV Data Directory'),
            description=self.config.get('description', f'CSV files in {self.data_dir}'),
            tables=tables,
            connection_info={'data_dir': str(self.data_dir)},
            last_indexed=datetime.now()
        )
    
    async def get_table_schema(self, table_name: str) -> TableMetadata:
        """Get schema for a specific CSV file."""
        csv_path = self.data_dir / f"{table_name}.csv"
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        columns = []
        rows = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if rows:
            
                for col_name in (reader.fieldnames or []):
                
                    sample_values = []
                    for i, row in enumerate(rows[:3]):
                        if row.get(col_name):
                            sample_values.append(row[col_name])
                    
                    columns.append(ColumnMetadata(
                        name=col_name,
                        data_type='str',
                        nullable=True,
                        sample_values=sample_values[:3]
                    ))
        
        return TableMetadata(
            name=table_name,
            columns=columns,
            row_count=len(rows) if rows else 0
        )
    
    async def get_table_data(self, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample data from a CSV file."""
        csv_path = self.data_dir / f"{table_name}.csv"
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = []
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                rows.append(row)
        
        return rows